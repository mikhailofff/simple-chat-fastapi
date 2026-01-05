import 'react'
import {useState, useEffect, useRef, useCallback} from 'react'
import { useAuth } from '../../components/Auth/AuthProvider'

import {useApi} from '../../hooks/useApi.js'
import {useWebSocket} from '../../hooks/useWebSocket.js';

import styles from './ChatPage.module.css'

import ChatMessages from './ChatMessages.jsx'
import ChatInput from './ChatInput.jsx'
import ChatSidebar from './ChatSidebar.jsx'

import {parseTimestamp, shouldShowDateHeader} from '../../utils/dateUtils.js'

export function Chat() {
	const [messages, setMessages] = useState([]);
	const messagesRef = useRef(messages);
	const [loading, setLoading] = useState(false);
    const [hasMore, setHasMore] = useState(true);
	const chatContainerRef = useRef(null);
	const messagesEndRef = useRef(null);
	const [inputValue, setInputValue] = useState('');
	const inputRef = useRef(null);
	const { user } = useAuth();
	const username = user?.username || "";
	const [onlineUsers, setOnlineUsers] = useState(0);
	const dateHeadersCreatedRef = useRef(new Set());
	const onMessage = useCallback(
		(msg) => {
			setMessages(prev => [...prev, msg]);

			if(msg.sender === '<DateHeader>' && msg.timestamp) {
				const headerDate = new Date(msg.timestamp);
				if (!isNaN(headerDate.getTime())) {
					dateHeadersCreatedRef.current.add(headerDate.toDateString());
				}
			}
		},
		[]
	);
	const onOnlineCount = useCallback(
		(count) => setOnlineUsers(count),
		[]
	);
	const {ws, sendMessage, userlist, } = useWebSocket({
		username: username,
		onMessage, 
		onOnlineCount,
		dateHeadersCreated: dateHeadersCreatedRef.current,
	  });
	const {makeRequest} = useApi()

	useEffect(() => {
		const loadMessages = async () => {
			try {
				const data = Object.values(await makeRequest("messages", { method: "GET" }))[0];
				const formattedMessages = [];
				let lastDate = null;

				data.forEach(element => {
					const messageDate = parseTimestamp(element.created_at);
					const updatedAtParsed = element.updated_at ? parseTimestamp(element.updated_at) : null;

					formattedMessages.push({
						id: element.id,
						text: element.content,
						timestamp: messageDate.toLocaleTimeString(),
						created_at: element.created_at,
						updatedAt: updatedAtParsed ? updatedAtParsed.toLocaleTimeString() : null,
						sender: element.created_by,
					});
				})
				setMessages(prev => {
					const combined = [...prev, ...formattedMessages]; 
					return insertDateHeaders(combined);
				});

				setTimeout(() => {
					messagesEndRef.current?.scrollIntoView({ behavior: "smooth", block: "end", inline: "nearest" });
				}, 100);                  
			} catch (err) {
				console.error("Error with receiving the messages:", err.message || "Didn't manage to load the messages.");
			}
		};
	
		loadMessages();
	}, []);

	useEffect(() => {
		messagesRef.current = messages;
	}, [messages]);
	
	useEffect(() => {
		const lastMessage = messages[messages.length - 1];
			if (lastMessage && lastMessage.sender === username) {
			setTimeout(() => {
				messagesEndRef.current?.scrollIntoView({ behavior: "smooth", block: "end", inline: "nearest" });
			}, 100);
		}
	}, [messages,  username]);

	const handleScroll = useCallback(() => {
		const container = chatContainerRef.current;
		if (container.scrollTop === 0 && !loading && hasMore) {
			if(messagesRef.current.length > 0) {
				loadOlderMessages();
			}
		}
	}, [loading, hasMore]);

	const loadOlderMessages = async () => {
		setLoading(true);
		const firstMessage = messagesRef.current[1]; 
		const lastId = firstMessage ? firstMessage.id : null;
	
		try {
			const params = new URLSearchParams();
			if (lastId !== null) params.append('last_id', lastId);
			params.append('limit', 20);

			const response = await makeRequest(`messages?${params.toString()}`, {
				method: "GET",
			});
			const olderMessages = response.messages.map(element => ({
				id: element.id,
				text: element.content,
				timestamp: parseTimestamp(element.created_at).toLocaleTimeString(),
				created_at: element.created_at,
				updatedAt: element.updated_at ? parseTimestamp(element.updated_at).toLocaleTimeString() : null,
				sender: element.created_by,
			  }));
	
			if (olderMessages.length < 20) {
				setHasMore(false);
			}
	
			setMessages(prev => {
				const combined = [...olderMessages, ...prev];
				return insertDateHeaders(combined);
			});
		} catch (err) {
			console.error("Failed to load older messages", err);
		} finally {
			setLoading(false);
		}
	};

	useEffect(() => {
		const container = chatContainerRef.current;
		if (container) {
		  container.addEventListener('scroll', handleScroll);
		}
		return () => {
		  if (container) {
			container.removeEventListener('scroll', handleScroll);
		  }
		};
	}, [handleScroll]);

	const insertDateHeaders = (messages) => {
		const filteredMessages = messages.filter(msg => msg.sender !== '<DateHeader>');
		const result = [];
		let lastDateString = null;
	  
		filteredMessages.forEach((msg) => {
			const messageDate = parseTimestamp(msg.created_at);
		  	if (!messageDate || isNaN(messageDate.getTime())) {
				result.push(msg);
				return;
		  	}
		  
		  	const messageDateStr = messageDate.toDateString();
	  
			if (messageDateStr !== lastDateString) {
				let timestamp;
				
				const today = new Date();
				const yesterday = new Date(today);
				yesterday.setDate(yesterday.getDate() - 1);
		
				if (messageDateStr === today.toDateString()) {
					timestamp = 'Today';
				} else if (messageDateStr === yesterday.toDateString()) {
					timestamp = 'Yesterday';
				} else {
					timestamp = messageDate.toLocaleDateString('en-US');
				}
	  
				result.push({
					text: null,
					timestamp: timestamp,
					sender: '<DateHeader>',
				});
				lastDateString = messageDateStr;
		  	}
	  
		  	result.push(msg);
		});
		
		return result;
	}

	const handleSendMessage = async () => {
		if (!inputValue.trim()) {
			inputRef.current?.focus();
			return;
		}

		const timestamp = new Date();

		try {
			const response = await makeRequest("send-message", {
				method: "POST",
				body: JSON.stringify({
					"content": inputValue,
					"created_at": timestamp,
					"created_by": username,
				}),
			});

			if(ws.current.readyState === WebSocket.OPEN) {
				sendMessage({
					"id": response.id,
					"content": inputValue,
					"created_at": timestamp,
					"created_by": username
				});
			}
			else {
				console.log("Error: Server is close but you're trying to send request");
			}
		} catch (err) {
			console.error("Failed to send message:", err);
		}

		setInputValue('');
	};

	const handleKeyDown = (event) => {
		if (event.key === 'Enter') {
			handleSendMessage();
		}
	};

	const handleDeleteMessage = async (messageId) => {
		if(!messageId) {
			console.log("Cannot delete message without ID");
			return;
		}

		try {
			await makeRequest("delete-message", {
				method: "DELETE",
				body: JSON.stringify({
					"id": messageId
				}),
			});
			setMessages(prev => prev.filter(message => message.id !== messageId));
		} catch(err) {
			console.error("Failed to delete message:", err);
		}
	};

	const handleUpdateMessage = async (messageId, newContent) => {
		if(!messageId) {
			console.log("Cannot update message without ID");
			return;
		}

		try {
			await makeRequest("update-message", {
				method: "PATCH",
				body: JSON.stringify({
					"id": messageId,
					"content": newContent
				}),
			});
			const nowLabel = new Date().toLocaleTimeString();
			setMessages(prev => prev.map(message => 
				message.id === messageId 
					? { ...message, text: newContent, updatedAt: nowLabel }
					: message
			));
		} catch(err) {
			console.error("Failed to update message:", err);
		}
	};

	return (
		<div className={styles['chat-main-layout']}>
			<div className={styles['chat-container']}>
				<div className={styles['messages-wrapper']}>
					<ChatMessages 
						messages={messages}
						user={username}
						messagesEndRef={messagesEndRef}
						onDeleteMessage={handleDeleteMessage}
						onUpdateMessage={handleUpdateMessage}
					/>
				</div>
				<ChatInput
					inputValue={inputValue}
					setInputValue={setInputValue}
					handleSendMessage={handleSendMessage}
					handleKeyDown={handleKeyDown}
					inputRef={inputRef}
				/>
			</div>
			<ChatSidebar onlineUsers={onlineUsers} userlist={userlist} />
		</div>
	);
}
