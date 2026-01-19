import { useState } from 'react'

import styles from './Message.module.css'

export default function Message({ user, text, sender, timestamp, updatedAt, onDelete, onUpdate, messageId }) {
    const [isHovered, setIsHovered] = useState(false);
    const [isEditing, setIsEditing] = useState(false);
    const [editText, setEditText] = useState(text);

    const handleDelete = (e) => {
        e.stopPropagation();
        if(onDelete && messageId) {
            const confirmed = window.confirm('Are you sure you want to delete this message?');
            if(confirmed) {
                onDelete(messageId);
            }
        }
    };

    const handleUpdate = (e) => {
        e.stopPropagation();
        if(onUpdate && messageId && editText.trim() !== text) {
            onUpdate(messageId, editText.trim());
            setIsEditing(false);
        } else if (editText.trim() === text) {
            setIsEditing(false);
        }
    };

    const handleEditClick = (e) => {
        e.stopPropagation();
        setIsEditing(true);
        setEditText(text);
    };

    const handleCancelEdit = (e) => {
        e.stopPropagation();
        setIsEditing(false);
        setEditText(text);
    };

    const handleKeyDown = (e) => {
        if (e.key === 'Enter') {
            handleUpdate(e);
        } else if (e.key === 'Escape') {
            handleCancelEdit(e);
        }
    };

    if (sender === '<System>') {
        return (
            <div className={`${styles['system-message']}`}>
                <div className={styles['message-text']}>{text}</div>
            </div>
        );
    }
    if (sender === '<DateHeader>') {
        return (
            <div className={`${styles['date-header']}`}>
                <div className={styles['date-text']}>{timestamp}</div>
            </div>
        );
    }

    return (
        <div 
            className={`${styles.message} ${user === sender ? styles['user-message'] : ''}`}
            onMouseEnter={() => setIsHovered(true)}
            onMouseLeave={() => setIsHovered(false)}    
            style={{ position: 'relative' }}
        >
            {isHovered && (user === sender) && !isEditing && (
                <div className={styles.actionButtons}>
                    <button
                        className={styles.updateButton}
                        onClick={handleEditClick}
                        title="Edit message"
                        aria-label='Edit message'
                    >
                        ✏️
                    </button>
                    <button
                        className={styles.deleteButton}
                        onClick={handleDelete}
                        title="Delete message"
                        aria-label='Delete message'
                    >
                        ×
                    </button>
                </div>
            )}
            <div className={styles['message-info']}>
                <span className={styles.sender}>{sender}</span>
                <span className={styles.timestamp}>
                    {timestamp}
                    {updatedAt && (
                        <span className={styles.editedLabel} title={`Edited at ${updatedAt}`}>
                            · edited {updatedAt}
                        </span>
                    )}
                </span>
            </div>
            {isEditing ? (
                <div className={styles.editContainer}>
                    <input
                        type="text"
                        value={editText}
                        onChange={(e) => setEditText(e.target.value)}
                        onKeyDown={handleKeyDown}
                        className={styles.editInput}
                        autoFocus
                    />
                    <div className={styles.editButtons}>
                        <button
                            className={styles.saveButton}
                            onClick={handleUpdate}
                            title="Save changes"
                        >
                            ✓
                        </button>
                        <button
                            className={styles.cancelButton}
                            onClick={handleCancelEdit}
                            title="Cancel edit"
                        >
                            ✕
                        </button>
                    </div>
                </div>
            ) : (
                <div className={styles['message-text']}>{text}</div>
            )}
        </div>
    );
};
