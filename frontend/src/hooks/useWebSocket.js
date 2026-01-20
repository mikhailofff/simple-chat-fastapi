import { useEffect, useRef, useState } from 'react';

import { parseTimestamp } from '../utils/dateUtils';

import { WS_BASE_URL } from '../config/api';

export function useWebSocket({ username, onMessage, onOnlineCount, hasTodayMessagesRef }) {
    const ws = useRef(null);
    const [userlist, setUserlist] = useState([])
    const onMessageRef = useRef(onMessage);
    const onOnlineCountRef = useRef(onOnlineCount);
    const lastDateRef = useRef(null);

    useEffect(() => { onMessageRef.current = onMessage }, [onMessage]);
    useEffect(() => { onOnlineCountRef.current = onOnlineCount }, [onOnlineCount]);

    useEffect(() => {
        ws.current = new WebSocket(WS_BASE_URL + username);

        ws.current.onopen = () => {
            const newMessage = {
                sender: '<System>',
                text: `User ${username} entered the chat`,
                timestamp: null,
            };
            ws.current.send(
                JSON.stringify({
                    content: newMessage.text,
                    created_at: newMessage.timestamp,
                    created_by: newMessage.sender,
                })
            );
        };

        ws.current.onmessage = (event) => {
            const eventJSON = JSON.parse(event.data);
            if(eventJSON.userlist) {
                var userlist = Object.keys(eventJSON.userlist).map((key) => [key, eventJSON.userlist[key]]);
                onOnlineCountRef.current && onOnlineCountRef.current(userlist.length);
                setUserlist(eventJSON.userlist)
                return;
            }
            if(eventJSON.content != `User ${username} entered the chat`) {
                const parsedDate = parseTimestamp(eventJSON.created_at);
                const currentDate = parsedDate ? new Date(
                    parsedDate.getFullYear(),
                    parsedDate.getMonth(),
                    parsedDate.getDate()
                ) : null;

                const shouldShowDateHeader = currentDate &&
                    (!lastDateRef.current || currentDate.getTime() !== lastDateRef.current.getTime()) &&
                    !hasTodayMessagesRef.current;

                if(shouldShowDateHeader) {
                    lastDateRef.current = currentDate;

                    let timestamp;

                    const today = new Date();
                    const yesterday = new Date(today);
                    yesterday.setDate(yesterday.getDate() - 1);

                    if(today.toDateString() === parsedDate.toDateString()) {
                        timestamp = 'Today';
                    }
                    else if(yesterday.toDateString() === parsedDate.toDateString()) {
                        timestamp = 'Yesterday';
                    }
                    else {
                        timestamp = parsedDate.toLocaleDateString('en-US');
                    }

                    onMessageRef.current && onMessageRef.current({
                        id: null,
                        text: null,
                        timestamp: timestamp,
                        sender: '<DateHeader>',
                    });
                }

                const timestamp = (parsedDate) ? parsedDate.toLocaleTimeString() : eventJSON.created_at;
                onMessageRef.current && onMessageRef.current({
                    id: eventJSON.id || null,
                    text: eventJSON.content,
                    timestamp: timestamp,
                    sender: eventJSON.created_by,
                });
            }
        };

        const handleBeforeUnload = () => {
            if (ws.current && ws.current.readyState === WebSocket.OPEN) {
                const newMessage = {
                    id: null,
                    sender: '<System>',
                    text: `User ${username} left the chat`,
                    timestamp: null,
                };
                ws.current.send(
                    JSON.stringify({
                        content: newMessage.text,
                        created_at: newMessage.timestamp,
                        created_by: newMessage.sender,
                    })
                );
            }
        };

        window.addEventListener('beforeunload', handleBeforeUnload);

        return () => {
            window.removeEventListener('beforeunload', handleBeforeUnload);
            if (ws.current) {
                ws.current.onopen = null;
                ws.current.onmessage = null;
                ws.current.close();
            }
        };
    }, [username]);

    const sendMessage = (msgObj) => {
        if (ws.current && ws.current.readyState === WebSocket.OPEN) {
            ws.current.send(JSON.stringify(msgObj));
        }
    };

    return { ws, sendMessage, userlist };
}
