import styles from './ChatPage.module.css'

export default function ChatInput({ inputValue, setInputValue, handleSendMessage, handleKeyDown, inputRef }) {
	return (
		<div className={styles['input-panel']}>
			<input
				ref={inputRef}
				type="text"
				value={inputValue}
				onChange={(e) => setInputValue(e.target.value)}
				onKeyDown={handleKeyDown}
				placeholder="Write message..."
				autoFocus={true}
			/>
			<button onClick={handleSendMessage}>Send</button>
		</div>
	);
}
