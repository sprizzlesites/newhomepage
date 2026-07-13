 <a href="#" id="back-link">
        <img class="brand-logo" src="assets/favicon.svg" alt="Sprizzle">
        </a>
        <span>Audio</span>
        <script>
document.getElementById('back-link').addEventListener('click', function(event) {
    // Prevent the default behavior of jumping to the top of the page (#)
    event.preventDefault(); 
    
    // Trigger the native browser back action
    window.history.back(); 
});
</script>
