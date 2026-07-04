document.querySelectorAll('.local-datetime').forEach(el => {
    const utc = el.getAttribute('datetime');
    if (!utc) return;

    const localDate = new Date(utc);

    el.textContent = localDate.toLocaleString(); 
});