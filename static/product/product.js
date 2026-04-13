document.addEventListener('DOMContentLoaded', () => {
    const commentListContainer = document.getElementById('commentListContainer');
    const commentsPagination = document.querySelector('.comments-pagination');
    
    if (commentsPagination) {
        const paginationButtons = commentsPagination.querySelectorAll('[data-page]');
        paginationButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                preventPageJump(e);  // Use shared utility to prevent page jump
                const page = btn.getAttribute('data-page');
                loadCommentsPage(page);
            });
        });
    }

    function loadCommentsPage(page) {
        const productId = CURRENT_PRODUCT_ID;
        const endpoint = `/get_comments/${productId}?page=${page}`;
        
        fetch(endpoint)
            .then(response => response.json())
            .then(data => {
                // Update comments HTML
                commentListContainer.innerHTML = data.html;
                
                // Update pagination using shared utility
                if (commentsPagination) {
                    updatePaginationControls(data, commentsPagination, endpoint, (page) => {
                        loadCommentsPage(page);
                    });
                }
            })
            .catch(error => console.error('Error loading comments:', error));
    }
    
    // 1. QUANTITY SELECTOR
    const minusBtn = document.getElementById("minusBtn");
    const plusBtn = document.getElementById("plusBtn");
    const qtyInput = document.getElementById("qtyInput");

    if(minusBtn && plusBtn && qtyInput) {
        minusBtn.onclick = () => {
            if (qtyInput.value > 1) qtyInput.value--;
        };
        plusBtn.onclick = () => {
            qtyInput.value++;
        };
    }

    // 2. ACCORDION LOGIC
    const accordions = document.querySelectorAll('.accordion-header');

    accordions.forEach(acc => {
        acc.addEventListener('click', function() {
            this.classList.toggle('active');
            
            // Toggle panel visibility
            const panel = this.nextElementSibling;
            if (panel.style.maxHeight) {
                panel.style.maxHeight = null;
                this.setAttribute('aria-expanded', 'false');
            } else {
                // Close others if you want only one open at a time (Optional)
                // closeAllAccordions(); 
                
                panel.style.maxHeight = panel.scrollHeight + "px";
                this.setAttribute('aria-expanded', 'true');
            }
        });
    });

    // 3. AJAX COMMENT SUBMISSION
    const commentForm = document.getElementById('commentFormAjax');
    const commentList = document.getElementById('commentListContainer');
    const commentInput = document.getElementById('commentText');

    if (commentForm) {
        commentForm.addEventListener('submit', function (e) {
            e.preventDefault();

            // Basic validation
            if(!commentInput.value.trim()) return;

            const formData = new FormData(commentForm);

            // Using the global variable set in HTML
            fetch(`/post_comment/${CURRENT_PRODUCT_ID}`, {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    // Create new review element with Elite styling
                    const newReviewHTML = `
                        <div class="review-card" style="animation: fadeIn 0.5s ease;">
                            <div class="review-header">
                                <span class="reviewer-name">${data.user_name}</span>
                                <span class="review-date">${data.date}</span>
                            </div>
                            <p class="review-body">${data.content}</p>
                        </div>
                    `;
                    
                    // Insert at top
                    commentList.insertAdjacentHTML('afterbegin', newReviewHTML);
                    commentInput.value = '';
                    
                    // Auto-expand the accordion if needed (it should be open to submit)
                    const panel = commentForm.closest('.accordion-content');
                    if(panel) {
                        panel.style.maxHeight = panel.scrollHeight + "px";
                    }

                } else {
                    alert(data.message || "An error occurred.");
                }
            })
            .catch(error => console.error('Error:', error));
        });
    }

});

function handleCart(productId, actionType) {
    const quantity = document.getElementById('qtyInput').value;
    
    // Tạo form ẩn để submit
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = `/add-to-cart/${productId}`;
    form.style.display = 'none';
    
    // Thêm input cho action
    const actionInput = document.createElement('input');
    actionInput.type = 'hidden';
    actionInput.name = 'action';
    actionInput.value = actionType;
    form.appendChild(actionInput);
    
    // Thêm input cho quantity
    const quantityInput = document.createElement('input');
    quantityInput.type = 'hidden';
    quantityInput.name = 'quantity';
    quantityInput.value = quantity;
    form.appendChild(quantityInput);
    
    document.body.appendChild(form);
    form.submit();
}

