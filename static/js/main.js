// ========================= THEME MANAGEMENT =========================
function setTheme(theme) {
    document.body.className = theme;
    document.documentElement.className = theme;
    localStorage.setItem('theme', theme);
    
    // Save to database 
    fetch('/update-theme', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: 'theme=' + encodeURIComponent(theme)
    }).then(response => response.json())
      .then(data => {
          if (data.success) {
              console.log('Theme saved to database!');
          }
      })
      .catch(error => {
          console.error('Failed to save theme:', error);
      });
    
    // Update active state
    document.querySelectorAll('.theme-option').forEach(opt => {
        opt.classList.remove('active');
        if (opt.dataset.theme === theme) {
            opt.classList.add('active');
        }
    });
}

// Apply theme IMMEDIATELY before page renders (prevents flash)
(function() {
    const savedTheme = localStorage.getItem('theme') || 'theme-light';
    document.documentElement.className = savedTheme;
})();

// ========================= MENU & MODAL MANAGEMENT =========================
function toggleMenu() {
    const menu = document.getElementById('mainMenu');
    menu.classList.toggle('active');
}

function toggleAddMenu() {
    const menu = document.getElementById('addMenu');
    menu.classList.toggle('active');
}

function openModal(modalId) {
    closeAllModals();
    document.getElementById('modalOverlay').classList.add('active');
    document.getElementById(modalId).style.display = 'block';
}

function openThemeModal() { openModal('themeModal'); }
function openSettingsModal() { openModal('settingsModal'); }
function openExportModal() { openModal('exportModal'); }
function openStatsModal() { openModal('statsModal'); }
function openAddCategoryModal() { openModal('addCategoryModal'); }
function openAddTaskModal() { openModal('addTaskModal'); }
function openShareModal() { openModal('shareModal'); }

function closeAllModals() {
    document.getElementById('modalOverlay').classList.remove('active');
    document.querySelectorAll('.modal').forEach(m => m.style.display = 'none');
    document.getElementById('mainMenu').classList.remove('active');
    document.getElementById('addMenu').classList.remove('active');
}

// ========================= EXPORT PDF =========================
function exportPDF(type) {
    const form = document.getElementById('exportForm');
    const formData = new FormData(form);
    const categoryIds = formData.getAll('category_ids');
    
    // Get the base URLs from data attributes on the body
    const weekUrl = document.body.dataset.weekUrl || '';
    const monthUrl = document.body.dataset.monthUrl || '';
    const yearUrl = document.body.dataset.yearUrl || '';
    
    let url = '';
    if (type === 'weekly') {
        url = weekUrl;
    } else if (type === 'monthly') {
        url = monthUrl;
    } else if (type === 'yearly') {
        url = yearUrl;
    }
    
    // Add category IDs to URL
    if (categoryIds.length > 0) {
        const params = new URLSearchParams();
        categoryIds.forEach(id => params.append('category_ids', id));
        url += (url.includes('?') ? '&' : '?') + params.toString();
    }
    
    window.location.href = url;
    closeAllModals();
}

// ========================= SHARE PDF =========================
function createShareLink(pdfType) {
    const expiresIn = document.getElementById('shareExpires').value;
    
    // Navigate to create share link endpoint
    window.location.href = `/share/pdf/${pdfType}?expires=${expiresIn}`;
}

// ========================= DELETE CATEGORY =========================
function deleteCategory(categoryId, categoryName) {
    event.preventDefault();
    event.stopPropagation();
    
    if (confirm(`Delete category "${categoryName}" and ALL its tasks?\n\nThis action cannot be undone!`)) {
        document.getElementById("delete-category-id").value = categoryId;
        document.getElementById("delete-category-form").submit();
    }
}

// ========================= PROFILE MODAL =========================
function openProfileModal() { 
    openModal('profileModal'); 
}

// ========================= TUTORIAL SYSTEM =========================
let currentTutorialStep = 1;
const totalTutorialSteps = 4;

function showTutorial() {
    currentTutorialStep = 1;
    updateTutorialStep();
    openModal('tutorialModal');
}

function nextTutorialStep() {
    if (currentTutorialStep < totalTutorialSteps) {
        currentTutorialStep++;
        updateTutorialStep();
    } else {
        closeTutorial();
    }
}

function skipTutorial() {
    if (document.getElementById('dontShowTutorial').checked) {
        localStorage.setItem('tutorialCompleted', 'true');
    }
    closeTutorial();
}

function closeTutorial() {
    if (document.getElementById('dontShowTutorial').checked) {
        localStorage.setItem('tutorialCompleted', 'true');
    }
    closeAllModals();
}

function updateTutorialStep() {
    // Hide all steps
    document.querySelectorAll('.tutorial-step').forEach(step => {
        step.style.display = 'none';
    });
    
    // Show current step
    const currentStep = document.querySelector(`.tutorial-step[data-step="${currentTutorialStep}"]`);
    if (currentStep) {
        currentStep.style.display = 'block';
    }
    
    // Update button text
    const nextBtn = document.getElementById('tutorialNextBtn');
    if (currentTutorialStep === totalTutorialSteps) {
        nextBtn.textContent = 'Got it!';
    } else {
        nextBtn.textContent = 'Next';
    }
}

// ========================= INITIALIZATION =========================
document.addEventListener("DOMContentLoaded", function() {
    // Load saved theme on page load (apply to body as well)
    const savedTheme = localStorage.getItem('theme') || 'theme-light';
    document.body.className = savedTheme;
    
    // Set active theme option
    document.querySelectorAll('.theme-option').forEach(opt => {
        if (opt.dataset.theme === savedTheme) {
            opt.classList.add('active');
        }
    });

    // Disable autocomplete on all input fields
    document.querySelectorAll('input').forEach(input => {
        input.setAttribute('autocomplete', 'off');
    });

    // Close dropdowns when clicking outside
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.top-bar-right') && !e.target.closest('.floating-add')) {
            const menu = document.getElementById('mainMenu');
            const addMenu = document.getElementById('addMenu');
            if (menu) menu.classList.remove('active');
            if (addMenu) addMenu.classList.remove('active');
        }
    });

    // ========================= DELETE TASK (Long Press) =========================
    const LONG_PRESS_TIME = 600;
    let pressTimer = null;

    document.querySelectorAll('.task-item').forEach(item => {
        const taskId = item.dataset.taskId;

        // Desktop right-click
        item.addEventListener("contextmenu", function(e) {
            e.preventDefault();
            if (confirm("Delete this task?")) {
                document.getElementById("delete-task-id").value = taskId;
                document.getElementById("delete-form").submit();
            }
        });

        // Mobile long-press
        const startPress = (e) => {
            pressTimer = setTimeout(() => {
                if (confirm("Delete this task?")) {
                    document.getElementById("delete-task-id").value = taskId;
                    document.getElementById("delete-form").submit();
                }
            }, LONG_PRESS_TIME);
        };

        const cancelPress = () => {
            clearTimeout(pressTimer);
        };

        item.addEventListener("touchstart", startPress);
        item.addEventListener("touchend", cancelPress);
        item.addEventListener("touchmove", cancelPress);
        item.addEventListener("mousedown", startPress);
        item.addEventListener("mouseup", cancelPress);
        item.addEventListener("mouseleave", cancelPress);
    });

    // Check if tutorial should be shown
    const tutorialCompleted = localStorage.getItem('tutorialCompleted');
    const isNewUser = document.body.dataset.newUser === 'true';
    
    if (!tutorialCompleted && isNewUser) {
        setTimeout(() => {
            showTutorial();
        }, 1000); // Show after 1 second
    }
});