import Message from '../../components/Message/Message.jsx'
import styles from './ChatPage.module.css'

export default function ChatMessages({ messages, user, messagesEndRef, onDeleteMessage, onUpdateMessage }) {
    return (
        <div className={styles['messages']}>
            {messages.map((msg, index) => (
                <Message
                    key={msg.id || index}
                    user={user}
                    text={msg.text}
                    sender={msg.sender}
                    timestamp={msg.timestamp}
                    updatedAt={msg.updatedAt}
                    messageId={msg.id}
                    onDelete={onDeleteMessage}
                    onUpdate={onUpdateMessage}
                />
            ))}
            <div ref={messagesEndRef} />
        </div>
    );
}
