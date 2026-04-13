//Notification
const flashMessages = document.querySelectorAll('.flash-message');
flashMessages.forEach(msg => {
    setTimeout(() => {
        msg.style.transition = "opacity 0.5s ease";
        msg.style.opacity = "0";
        setTimeout(() => msg.remove(), 500);
    }, 3000);
});

//Real-time
document.getElementById('currentYear').textContent = new Date().getFullYear();

const header = document.getElementById('mainHeader');
const menuTrigger = document.getElementById('menuTrigger');
const mainMenu = document.getElementById('mainMenuDropdown');
const menuOverlay = document.getElementById('menuOverlay');

// Function to toggle menu
function toggleMenu() {
    const isActive = mainMenu.classList.toggle('active');
    menuOverlay.classList.toggle('active');
    menuTrigger.classList.toggle('active');

    if (isActive) {
        header.classList.add("shrink");
    } else {
        if (window.scrollY <= 50) {
            header.classList.remove("shrink");
        }
    }
}

// Scroll
window.onscroll = function () {
    if (mainMenu.classList.contains('active')) {
        header.classList.add("shrink");
        return;
    }

    if (document.body.scrollTop > 50 || document.documentElement.scrollTop > 50) {
        header.classList.add("shrink");
    } else {
        header.classList.remove("shrink");
    }
};

// Event Listeners for Menu
menuTrigger.addEventListener('click', (e) => {
    e.stopPropagation();
    toggleMenu();
});

menuOverlay.addEventListener('click', () => {
    toggleMenu();
});

const menuLinks = mainMenu.querySelectorAll('a');
menuLinks.forEach(link => {
    link.addEventListener('click', () => {
        toggleMenu();
    });
});

//Search bar
(function () {
    const searchContainer = document.getElementById('searchContainer');
    const searchInput = document.getElementById('searchInput');
    const searchBtn = document.getElementById('searchBtn');

    if (!searchContainer || !searchInput || !searchBtn) return;

    function performSearch() {
        const query = searchInput.value.trim();
        if (query) {
            console.log("Searching for:", query);
        }
    }

    searchBtn.addEventListener('click', (e) => {
        if (!searchContainer.classList.contains('active')) {
            preventPageJump(e);
            searchContainer.classList.add('active');
            searchInput.focus();
        } else {
            if (searchInput.value.trim() === "") {
                preventPageJump(e);
                searchContainer.classList.remove('active');
            }
        }
    });

    document.addEventListener('click', (e) => {
        if (!searchContainer.contains(e.target) && searchInput.value === "") {
            searchContainer.classList.remove('active');
        }
    });

    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            performSearch();
        }
    });
})();