async function showCopyLink(url) {
    const input = document.getElementById('share-link')
    const shareModal = document.getElementById('share_modal')

    input.value = url
    shareModal.showModal()
}

async function ShareLink() {
    if (navigator.share) {
        try {
            const input = document.getElementById('share-link')
            const button = document.getElementById('share-buuton')
            await navigator.clipboard.writeText(input.value);
            button.innerHTML = 'Copied'

            setTimeout(() => {
                button.innerHTML = 'Copy';
            }, 2000);
        } catch (err) {
            console.log('Share cancelled or failed');
        }
    } else {
        // Fallback: Copy to clipboard if Web Share API isn't supported
        navigator.clipboard.writeText(shareData.url);
    }

}