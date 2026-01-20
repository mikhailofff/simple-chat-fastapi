import styles from './User.module.css'

export default function User({ username }) {
    return (
        <div className={styles['user']}>{username}</div>
    );
}
