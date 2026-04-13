/**
 * Shared AJAX Pagination & Navigation Utility
 * Used by both product comments and category product listings
 * Eliminates duplicate fetch/pagination logic across pages
 * Also provides scroll prevention and navigation helpers
 */

/* ====== SCROLL & PAGE JUMP PREVENTION ====== */

/**
 * Prevent page from jumping back to top during AJAX operations
 * Call this when handling pagination/filtering clicks to stop default scroll behavior
 * @param {Event} event - The click/submit event
 */
function preventPageJump(event) {
    event.preventDefault();
}

/**
 * Save current scroll position before AJAX operation
 * Use with restoreScrollPosition() to maintain user's view
 * @returns {number} - Current scroll position
 */
function saveScrollPosition() {
    return window.scrollY || document.documentElement.scrollTop;
}

/**
 * Restore scroll position after AJAX operation
 * @param {number} position - The scroll position to restore
 * @param {number} smooth - If true, scroll smoothly; if false, instant (default: false)
 */
function restoreScrollPosition(position, smooth = false) {
    if (smooth) {
        window.scrollTo({ top: position, behavior: 'smooth' });
    } else {
        window.scrollTo(0, position);
    }
}

/**
 * Disable smooth scroll during AJAX to prevent jumpy behavior
 * Useful when you're updating DOM and want instant positioning
 */
function disableSmoothScroll() {
    const style = document.documentElement.style;
    const original = style.scrollBehavior;
    style.scrollBehavior = 'auto';
    return () => { style.scrollBehavior = original; }; // Return restore function
}

/**
 * Generic AJAX fetch for paginated content
 * @param {string} endpoint - The URL endpoint to fetch from
 * @param {string} contentSelector - CSS selector for content container
 * @param {string} paginationSelector - CSS selector for pagination controls
 * @param {Function} onSuccess - Optional callback after successful load
 */
function loadPaginatedContent(endpoint, contentSelector, paginationSelector, onSuccess) {
    fetch(endpoint)
        .then(response => response.json())
        .then(data => {
            const contentContainer = document.querySelector(contentSelector);
            if (contentContainer && data.html) {
                contentContainer.innerHTML = data.html;
            }
            
            const paginationContainer = document.querySelector(paginationSelector);
            if (paginationContainer) {
                updatePaginationControls(data, paginationContainer, endpoint.split('?')[0], onSuccess);
            }
            
            if (onSuccess) onSuccess(data);
        })
        .catch(error => console.error('Error loading paginated content:', error));
}

/**
 * Rebuild pagination controls dynamically
 * @param {Object} data - Response data with pagination info
 * @param {HTMLElement} container - Container for pagination buttons
 * @param {string} baseEndpoint - Base endpoint for pagination links
 * @param {Function} onButtonClick - Callback when pagination button is clicked
 */
function updatePaginationControls(data, container, baseEndpoint, onButtonClick) {
    let paginationHTML = '';
    
    // Previous button
    if (data.has_prev) {
        paginationHTML += `<button class="pagination-link" data-page="${data.prev_num}">← Previous</button>`;
    }
    
    // Page numbers
    for (let i = 1; i <= data.total_pages; i++) {
        if (i === data.current_page) {
            paginationHTML += `<span class="pagination-page active">${i}</span>`;
        } else {
            paginationHTML += `<button class="pagination-page" data-page="${i}">${i}</button>`;
        }
    }
    
    // Next button
    if (data.has_next) {
        paginationHTML += `<button class="pagination-link" data-page="${data.next_num}">Next →</button>`;
    }
    
    // Optional page indicator
    if (data.total_pages) {
        paginationHTML += `<span class="page-indicator">Page ${data.current_page} of ${data.total_pages}</span>`;
    }
    
    container.innerHTML = paginationHTML;
    
    // Reattach event listeners to new buttons
    const paginationButtons = container.querySelectorAll('[data-page]');
    paginationButtons.forEach(btn => {
        btn.addEventListener('click', (e) => {
            preventPageJump(e);  // Use shared utility
            const page = btn.getAttribute('data-page');
            if (onButtonClick) {
                onButtonClick(page);
            }
        });
    });
}

/**
 * Build query string from form data
 * Used by category filters to preserve filter state during pagination
 * @param {FormElement} form - The filter form
 * @param {Object} additionalParams - Additional parameters to add (like page, per_page)
 * @returns {string} - Query string for URL
 */
function buildQueryString(form, additionalParams = {}) {
    const formData = new FormData(form);
    const params = new URLSearchParams(formData);
    
    // Add any additional parameters
    Object.entries(additionalParams).forEach(([key, value]) => {
        params.set(key, value);
    });
    
    return params.toString();
}

/**
 * Parse HTML response and extract specific element
 * Useful when server returns full HTML and we need specific sections
 * @param {string} html - HTML string to parse
 * @param {string} selector - CSS selector for element to extract
 * @returns {HTMLElement|null} - The extracted element or null
 */
function extractElementFromHTML(html, selector) {
    const parser = new DOMParser();
    const doc = parser.parseFromString(html, 'text/html');
    return doc.querySelector(selector);
}
