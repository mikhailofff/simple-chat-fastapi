import User from '../../components/User/User.jsx'
import styles from './ChatPage.module.css'

export default function ChatSidebar({ onlineUsers, userlist }) {
    return (
        <div className={styles['userlist-frame']}>
            <div className={styles['online-users']}>
                <span className={styles['online-users-label']}>Online Users ({onlineUsers})</span>
            </div>

            <hr className={styles['userlist-separator']} />

            <div className={styles['userlist']}>
                {userlist.map((user, index) => (
                    <User key={index} username={user} />
                ))}
            </div>
        </div>
    );
}
