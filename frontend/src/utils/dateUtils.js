export function parseTimestamp(timestamp) {
    if(!timestamp) return null;

    try {
        const date = new Date(timestamp);
        return isNaN(date.getTime()) ? null : date;
    } catch(error) {
        console.warn('Failed to parse timestamp:', timestamp);
        return null;
    }
}

export function shouldShowDateHeader(currentDate, previousDate) {
    if (!currentDate) return false;
    if (!previousDate) return true;

    return currentDate.toDateString() !== previousDate.toDateString();
}
