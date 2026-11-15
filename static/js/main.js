/**
 * SocialSphere — Interactive Vanilla JavaScript Core
 */

document.addEventListener('DOMContentLoaded', () => {
  initCsrfProtection();
  initLikeButtons();
  initDoubleTapLike();
  initFollowButtons();
  initCreatePostModal();
  initProfileTabs();
  initAutoDismissAlerts();
  initPasswordToggles();
  initProfilePicturePreview();
  initBioCharacterCounter();
});

/**
 * 1. CSRF Token Retrieval Helper
 */
function getCsrfToken() {
  const metaToken = document.querySelector('meta[name="csrf-token"]');
  if (metaToken && metaToken.content) {
    return metaToken.content;
  }
  const match = document.cookie.match(/csrftoken=([^;]+)/);
  return match ? match[1] : '';
}

function initCsrfProtection() {
  // Ensure all fetch calls can easily attach the CSRF header
  window.csrfToken = getCsrfToken();
}

/**
 * 2. AJAX Like Button Handler
 */
function initLikeButtons() {
  document.querySelectorAll('.like-btn').forEach(btn => {
    btn.addEventListener('click', async (e) => {
      // If inside an anchor tag (unauthenticated), allow redirect to login
      if (btn.tagName.toLowerCase() === 'a') return;

      e.preventDefault();
      const postId = btn.getAttribute('data-post-id');
      if (!postId) return;

      try {
        const response = await fetch(`/post/${postId}/like/`, {
          method: 'POST',
          headers: {
            'X-CSRFToken': getCsrfToken(),
            'X-Requested-With': 'XMLHttpRequest',
            'Accept': 'application/json'
          }
        });

        if (response.ok) {
          const data = await response.json();
          if (data.success) {
            btn.classList.toggle('liked', data.is_liked);
            const countEl = document.getElementById(`likes-count-${postId}`);
            if (countEl) {
              countEl.textContent = data.likes_count;
            }
          }
        }
      } catch (err) {
        console.error('Error toggling like:', err);
      }
    });
  });
}

/**
 * 3. Instagram-style Double-Click Media to Like with Heart Burst
 */
function initDoubleTapLike() {
  document.querySelectorAll('.post-media-container').forEach(mediaContainer => {
    let lastTap = 0;
    const postId = mediaContainer.getAttribute('data-post-id');
    const burstHeart = mediaContainer.querySelector('.like-heart-burst');

    const triggerHeartPop = () => {
      if (burstHeart) {
        burstHeart.classList.remove('animate');
        void burstHeart.offsetWidth; // Trigger DOM reflow
        burstHeart.classList.add('animate');
        setTimeout(() => {
          burstHeart.classList.remove('animate');
        }, 800);
      }

      // If user is authenticated, trigger like
      const likeBtn = document.querySelector(`.like-btn[data-post-id="${postId}"]`);
      if (likeBtn && !likeBtn.classList.contains('liked')) {
        likeBtn.click();
      }
    };

    // Desktop double click
    mediaContainer.addEventListener('dblclick', (e) => {
      e.preventDefault();
      triggerHeartPop();
    });

    // Mobile double tap
    mediaContainer.addEventListener('touchend', (e) => {
      const currentTime = new Date().getTime();
      const tapLength = currentTime - lastTap;
      if (tapLength < 300 && tapLength > 0) {
        e.preventDefault();
        triggerHeartPop();
      }
      lastTap = currentTime;
    });
  });
}

/**
 * 4. AJAX Follow Toggle Button Handler
 */
function initFollowButtons() {
  document.querySelectorAll('.inline-follow-form').forEach(form => {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const username = form.getAttribute('data-username');
      const submitBtn = form.querySelector('button[type="submit"]');
      if (!username || !submitBtn) return;

      submitBtn.disabled = true;

      try {
        const response = await fetch(`/social/follow/${username}/`, {
          method: 'POST',
          headers: {
            'X-CSRFToken': getCsrfToken(),
            'X-Requested-With': 'XMLHttpRequest',
            'Accept': 'application/json'
          }
        });

        if (response.ok) {
          const data = await response.json();
          if (data.success) {
            if (data.is_following) {
              submitBtn.textContent = 'Following';
              submitBtn.classList.remove('btn-gradient');
              submitBtn.classList.add('btn-secondary');
            } else {
              submitBtn.textContent = 'Follow';
              submitBtn.classList.remove('btn-secondary');
              submitBtn.classList.add('btn-gradient');
            }

            // If on target user's profile, update followers count
            const followersEl = document.getElementById('profile-followers-count');
            if (followersEl) {
              followersEl.textContent = data.followers_count;
            }
          }
        }
      } catch (err) {
        console.error('Error toggling follow:', err);
      } finally {
        submitBtn.disabled = false;
      }
    });
  });
}

/**
 * 5. Create Post Modal & Image Drag/Drop Preview
 */
function initCreatePostModal() {
  const modal = document.getElementById('create-post-modal');
  if (!modal) return;

  const openBtns = document.querySelectorAll('.open-create-modal-btn');
  const closeBtn = document.getElementById('close-post-modal-btn');
  const cancelBtn = document.getElementById('cancel-post-modal-btn');
  const fileInput = document.getElementById('modal-image-input');
  const dropzone = document.getElementById('upload-dropzone');
  const previewContainer = document.getElementById('dropzone-preview-container');
  const previewImg = document.getElementById('image-preview');
  const placeholder = document.getElementById('dropzone-placeholder');
  const removePreviewBtn = document.getElementById('remove-preview-btn');

  const openModal = () => {
    modal.classList.add('active');
    modal.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';
  };

  const closeModal = () => {
    modal.classList.remove('active');
    modal.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
  };

  openBtns.forEach(btn => btn.addEventListener('click', openModal));
  if (closeBtn) closeBtn.addEventListener('click', closeModal);
  if (cancelBtn) cancelBtn.addEventListener('click', closeModal);

  // Close on outside click
  modal.addEventListener('click', (e) => {
    if (e.target === modal) closeModal();
  });

  // Close on Escape key
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && modal.classList.contains('active')) {
      closeModal();
    }
  });

  // Image Upload Preview Handling
  const displayImagePreview = (file) => {
    if (file && file.type.startsWith('image/')) {
      const reader = new FileReader();
      reader.onload = (e) => {
        previewImg.src = e.target.result;
        previewContainer.classList.remove('hidden');
        placeholder.classList.add('hidden');
      };
      reader.readAsDataURL(file);
    }
  };

  if (fileInput) {
    fileInput.addEventListener('change', (e) => {
      if (e.target.files && e.target.files[0]) {
        displayImagePreview(e.target.files[0]);
      }
    });
  }

  if (removePreviewBtn) {
    removePreviewBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      if (fileInput) fileInput.value = '';
      previewImg.src = '';
      previewContainer.classList.add('hidden');
      placeholder.classList.remove('hidden');
    });
  }

  // Drag & drop support
  if (dropzone) {
    ['dragenter', 'dragover'].forEach(eventName => {
      dropzone.addEventListener(eventName, (e) => {
        e.preventDefault();
        dropzone.classList.add('dragover');
      });
    });

    ['dragleave', 'drop'].forEach(eventName => {
      dropzone.addEventListener(eventName, (e) => {
        e.preventDefault();
        dropzone.classList.remove('dragover');
      });
    });

    dropzone.addEventListener('drop', (e) => {
      if (e.dataTransfer.files && e.dataTransfer.files[0]) {
        fileInput.files = e.dataTransfer.files;
        displayImagePreview(e.dataTransfer.files[0]);
      }
    });
  }

  // Focus comment input when comment button is clicked
  document.querySelectorAll('.comment-focus-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const postId = btn.getAttribute('data-post-id');
      const card = document.getElementById(`post-card-${postId}`);
      if (card) {
        const input = card.querySelector('.comment-text-input');
        if (input) input.focus();
      }
    });
  });
}

/**
 * 6. Profile Tabs Navigation
 */
function initProfileTabs() {
  const tabs = document.querySelectorAll('.profile-tab');
  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      tabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
    });
  });
}

/**
 * 7. Auto-Dismiss Alert Toasts
 */
function initAutoDismissAlerts() {
  document.querySelectorAll('.alert-toast').forEach(toast => {
    setTimeout(() => {
      toast.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(-10px)';
      setTimeout(() => toast.remove(), 400);
    }, 4500);
  });
}

/**
 * 8. Password Visibility Toggle
 */
function initPasswordToggles() {
  document.querySelectorAll('.password-toggle-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const targetId = btn.getAttribute('data-target');
      if (!targetId) return;

      const input = document.getElementById(targetId);
      if (!input) return;

      const eyeOpen = btn.querySelector('.eye-open');
      const eyeClosed = btn.querySelector('.eye-closed');

      if (input.type === 'password') {
        input.type = 'text';
        if (eyeOpen) eyeOpen.classList.add('hidden');
        if (eyeClosed) eyeClosed.classList.remove('hidden');
        btn.setAttribute('aria-label', 'Hide password');
      } else {
        input.type = 'password';
        if (eyeOpen) eyeOpen.classList.remove('hidden');
        if (eyeClosed) eyeClosed.classList.add('hidden');
        btn.setAttribute('aria-label', 'Show password');
      }
    });
  });
}

/**
 * 9. Profile Picture Live Preview in Edit Profile
 */
function initProfilePicturePreview() {
  const fileInput = document.getElementById('edit-profile-picture-input');
  const previewImg = document.getElementById('avatar-preview-element');

  if (fileInput && previewImg) {
    fileInput.addEventListener('change', () => {
      if (fileInput.files && fileInput.files[0]) {
        const file = fileInput.files[0];
        if (file.type.startsWith('image/')) {
          const reader = new FileReader();
          reader.onload = (e) => {
            previewImg.src = e.target.result;
          };
          reader.readAsDataURL(file);
        }
      }
    });
  }
}

/**
 * 10. Live Biography Character Counter
 */
function initBioCharacterCounter() {
  const bioInput = document.getElementById('edit-bio');
  const counter = document.getElementById('bio-char-count');

  if (bioInput && counter) {
    const updateCount = () => {
      const length = bioInput.value.length;
      counter.textContent = `${length} / 350`;
      if (length >= 340) {
        counter.style.color = 'var(--color-danger)';
      } else {
        counter.style.color = 'var(--color-text-muted)';
      }
    };

    bioInput.addEventListener('input', updateCount);
    updateCount();
  }
}
