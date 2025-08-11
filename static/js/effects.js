// Cursor effects
document.addEventListener('DOMContentLoaded', function() {
    const cursorFollower = document.querySelector('.cursor-follower');
    const cursorDot = document.querySelector('.cursor-dot');
    
    // Check if device is mobile
    const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) || window.innerWidth <= 768;
    
    if (cursorFollower && !isMobile) {
        let mouseX = 0;
        let mouseY = 0;
        let followerX = 0;
        let followerY = 0;
        
        // Initialize cursor position
        cursorFollower.style.display = 'block';
        
        // Mouse move event
        document.addEventListener('mousemove', (e) => {
            mouseX = e.clientX;
            mouseY = e.clientY;
        });
        
        // Cursor animation loop
        function animateCursor() {
            // Smooth following for the magic wand
            followerX += (mouseX - followerX) * 0.30;
            followerY += (mouseY - followerY) * 0.30;
            
            cursorFollower.style.transform = `translate(${followerX}px, ${followerY}px)`;
            
            requestAnimationFrame(animateCursor);
        }
        
        animateCursor();
        
        // Show cursor immediately
        setTimeout(() => {
            cursorFollower.style.opacity = '1';
        }, 100);
        
        // Magic wand cursor effects on hoverable elements
        const hoverElements = document.querySelectorAll('a, button, .nav-link, .cta-button, .feature-card, .reel-card, .dropzone');
        
        hoverElements.forEach(element => {
            element.addEventListener('mouseenter', () => {
                cursorFollower.style.transform = `translate(${followerX}px, ${followerY}px) scale(1.3)`;
                cursorFollower.style.opacity = '1';
            });
            
            element.addEventListener('mouseleave', () => {
                cursorFollower.style.transform = `translate(${followerX}px, ${followerY}px) scale(1)`;
                cursorFollower.style.opacity = '1';
            });
        });
    }
    
    // Theme toggle functionality
    const themeToggle = document.getElementById('themeToggle');
    const html = document.documentElement;
    const themeIcon = themeToggle?.querySelector('i');
    
    // Load saved theme
    const savedTheme = localStorage.getItem('theme') || 'dark';
    html.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);
    
    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            const currentTheme = html.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            
            html.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            updateThemeIcon(newTheme);
            
            // Add transition effect
            html.style.transition = 'all 0.3s ease';
            setTimeout(() => {
                html.style.transition = '';
            }, 300);
        });
    }
    
    function updateThemeIcon(theme) {
        if (themeIcon) {
            themeIcon.className = theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
        }
    }
    
    // Parallax effect for liquid blobs and floating messages
    const liquidBlobs = document.querySelectorAll('.liquid-blob');
    const floatingMessages = document.querySelectorAll('.floating-message');
    
    window.addEventListener('scroll', () => {
        const scrolled = window.pageYOffset;
        const rate = scrolled * -0.5;
        
        liquidBlobs.forEach((blob, index) => {
            const speed = 0.5 + (index * 0.1);
            blob.style.transform = `translateY(${rate * speed}px) rotate(${scrolled * 0.1}deg)`;
        });
        
        // Add subtle parallax to floating messages
        floatingMessages.forEach((message, index) => {
            const speed = 0.2 + (index * 0.05);
            message.style.transform = `translateY(${rate * speed}px)`;
        });
    });
    
    // Add random sparkle effects to floating messages
    floatingMessages.forEach(message => {
        setInterval(() => {
            if (Math.random() > 0.7) {
                message.style.textShadow = '0 0 20px var(--accent-color)';
                message.style.transform = 'scale(1.1)';
                setTimeout(() => {
                    message.style.textShadow = '0 0 10px var(--accent-color)';
                    message.style.transform = 'scale(1)';
                }, 500);
            }
        }, 2000);
        
        // Add click interaction to floating messages
        message.addEventListener('click', () => {
            message.style.transform = 'scale(1.5) rotate(360deg)';
            message.style.textShadow = '0 0 30px var(--accent-color)';
            
            // Create burst effect
            for (let i = 0; i < 8; i++) {
                const burst = document.createElement('div');
                burst.innerHTML = '✨';
                burst.style.position = 'absolute';
                burst.style.fontSize = '1rem';
                burst.style.pointerEvents = 'none';
                burst.style.left = message.offsetLeft + message.offsetWidth / 2 + 'px';
                burst.style.top = message.offsetTop + message.offsetHeight / 2 + 'px';
                burst.style.zIndex = '9998';
                burst.style.transform = 'translate(-50%, -50%)';
                burst.style.transition = 'all 0.6s ease';
                
                document.body.appendChild(burst);
                
                const angle = (i / 8) * 360;
                const distance = 100;
                const vx = Math.cos(angle * Math.PI / 180) * distance;
                const vy = Math.sin(angle * Math.PI / 180) * distance;
                
                setTimeout(() => {
                    burst.style.transform = `translate(calc(-50% + ${vx}px), calc(-50% + ${vy}px)) scale(0)`;
                    burst.style.opacity = '0';
                    
                    setTimeout(() => {
                        if (document.body.contains(burst)) {
                            document.body.removeChild(burst);
                        }
                    }, 600);
                }, 50);
            }
            
            setTimeout(() => {
                message.style.transform = 'scale(1) rotate(0deg)';
                message.style.textShadow = '0 0 10px var(--accent-color)';
            }, 300);
        });
    });
    
    // Smooth reveal animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);
    
    // Observe elements for animation
    const animateElements = document.querySelectorAll('.feature-card, .showcase-image, .reel-card, .upload-container');
    animateElements.forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        el.style.transition = 'all 0.6s ease';
        observer.observe(el);
    });
    
    // Typing effect for hero title
    const heroTitle = document.querySelector('.hero-title');
    if (heroTitle) {
        const text = heroTitle.textContent;
        heroTitle.textContent = '';
        heroTitle.style.borderRight = '2px solid var(--accent-color)';
        
        let i = 0;
        const typeWriter = () => {
            if (i < text.length) {
                heroTitle.textContent += text.charAt(i);
                i++;
                setTimeout(typeWriter, 100);
            } else {
                heroTitle.style.borderRight = 'none';
            }
        };
        
        // Start typing effect after a short delay
        setTimeout(typeWriter, 500);
    }
    
    // Interactive hover effects for cards
    const cards = document.querySelectorAll('.feature-card, .reel-card');
    cards.forEach(card => {
        card.addEventListener('mousemove', (e) => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            
            const rotateX = (y - centerY) / 10;
            const rotateY = (centerX - x) / 10;
            
            card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateZ(10px)`;
        });
        
        card.addEventListener('mouseleave', () => {
            card.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) translateZ(0)';
        });
    });
    
    // Magic particle effect for buttons
    const buttons = document.querySelectorAll('.cta-button, .submit-btn');
    buttons.forEach(button => {
        button.addEventListener('click', (e) => {
            const rect = button.getBoundingClientRect();
            
            // Create magic sparkles
            for (let i = 0; i < 15; i++) {
                const sparkle = document.createElement('div');
                sparkle.innerHTML = ['✨', '🌟', '💫', '⭐', '🎆'][Math.floor(Math.random() * 5)];
                sparkle.style.position = 'absolute';
                sparkle.style.fontSize = '1.5rem';
                sparkle.style.pointerEvents = 'none';
                sparkle.style.left = rect.left + rect.width / 2 + 'px';
                sparkle.style.top = rect.top + rect.height / 2 + 'px';
                sparkle.style.zIndex = '9999';
                sparkle.style.transform = 'translate(-50%, -50%)';
                sparkle.style.transition = 'all 0.8s ease';
                
                document.body.appendChild(sparkle);
                
                const angle = (i / 15) * 360;
                const distance = 150 + Math.random() * 100;
                const vx = Math.cos(angle * Math.PI / 180) * distance;
                const vy = Math.sin(angle * Math.PI / 180) * distance;
                
                setTimeout(() => {
                    sparkle.style.transform = `translate(calc(-50% + ${vx}px), calc(-50% + ${vy}px)) scale(0)`;
                    sparkle.style.opacity = '0';
                    
                    setTimeout(() => {
                        if (document.body.contains(sparkle)) {
                            document.body.removeChild(sparkle);
                        }
                    }, 800);
                }, 50);
            }
            
            // Add magic wand wave effect
            const wandWave = document.createElement('div');
            wandWave.innerHTML = '🪶';
            wandWave.style.position = 'absolute';
            wandWave.style.fontSize = '3rem';
            wandWave.style.left = rect.left + rect.width / 2 + 'px';
            wandWave.style.top = rect.top + rect.height / 2 + 'px';
            wandWave.style.zIndex = '9999';
            wandWave.style.transform = 'translate(-50%, -50%) scale(0)';
            wandWave.style.transition = 'all 0.5s ease';
            
            document.body.appendChild(wandWave);
            
            setTimeout(() => {
                wandWave.style.transform = 'translate(-50%, -50%) scale(1) rotate(360deg)';
                setTimeout(() => {
                    wandWave.style.transform = 'translate(-50%, -50%) scale(0) rotate(720deg)';
                    setTimeout(() => {
                        if (document.body.contains(wandWave)) {
                            document.body.removeChild(wandWave);
                        }
                    }, 500);
                }, 300);
            }, 100);
        });
    });
    
    // Smooth scroll for navigation links
    const navLinks = document.querySelectorAll('a[href^="#"]');
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const targetId = link.getAttribute('href');
            const targetSection = document.querySelector(targetId);
            
            if (targetSection) {
                targetSection.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Loading animation for form submission
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', () => {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.classList.add('loading');
                submitBtn.disabled = true;
            }
        });
    });

    // Navbar dynamic text scaling effect
    const navbar = document.querySelector('.glass-nav');
    if (navbar && !isMobile) {
        const navLinks = navbar.querySelectorAll('.nav-link');
        const navbarBrand = navbar.querySelector('.navbar-brand');
        
        // Function to find closest text element to cursor
        function findClosestTextElement(mouseX, mouseY) {
            let closestElement = null;
            let closestDistance = Infinity;
            
            // Check nav links
            navLinks.forEach(link => {
                const rect = link.getBoundingClientRect();
                const centerX = rect.left + rect.width / 2;
                const centerY = rect.top + rect.height / 2;
                const distance = Math.sqrt((mouseX - centerX) ** 2 + (mouseY - centerY) ** 2);
                
                if (distance < closestDistance) {
                    closestDistance = distance;
                    closestElement = link;
                }
            });
            
            // Check navbar brand
            if (navbarBrand) {
                const rect = navbarBrand.getBoundingClientRect();
                const centerX = rect.left + rect.width / 2;
                const centerY = rect.top + rect.height / 2;
                const distance = Math.sqrt((mouseX - centerX) ** 2 + (mouseY - centerY) ** 2);
                
                if (distance < closestDistance) {
                    closestDistance = distance;
                    closestElement = navbarBrand;
                }
            }
            
            return closestElement;
        }
        
        // Mouse move event for dynamic scaling
        navbar.addEventListener('mousemove', (e) => {
            const closestElement = findClosestTextElement(e.clientX, e.clientY);
            
            // Reset all elements
            navLinks.forEach(link => {
                link.style.transform = 'scale(1)';
                link.style.textShadow = 'none';
                link.style.filter = 'brightness(1)';
            });
            
            if (navbarBrand) {
                navbarBrand.style.transform = 'scale(1)';
                navbarBrand.style.textShadow = 'none';
                navbarBrand.style.filter = 'brightness(1)';
            }
            
            // Apply effect to closest element
            if (closestElement) {
                const rect = closestElement.getBoundingClientRect();
                const centerX = rect.left + rect.width / 2;
                const centerY = rect.top + rect.height / 2;
                const distance = Math.sqrt((e.clientX - centerX) ** 2 + (e.clientY - centerY) ** 2);
                const maxDistance = 100; // Maximum distance for effect
                
                if (distance < maxDistance) {
                    const intensity = 1 - (distance / maxDistance);
                    const scale = 1 + (intensity * 0.15); // Scale up to 1.15
                    
                    closestElement.style.transform = `scale(${scale})`;
                    
                    // Add aura effect based on intensity
                    if (closestElement.classList.contains('nav-link')) {
                        const shadowIntensity = Math.floor(intensity * 30);
                        closestElement.style.textShadow = `
                            0 0 ${shadowIntensity}px var(--accent-color),
                            0 0 ${shadowIntensity * 1.5}px var(--accent-color),
                            0 0 ${shadowIntensity * 2}px var(--accent-color)
                        `;
                        closestElement.style.filter = `brightness(${1 + intensity * 0.3})`;
                    } else if (closestElement.classList.contains('navbar-brand')) {
                        const shadowIntensity = Math.floor(intensity * 35);
                        closestElement.style.textShadow = `
                            0 0 ${shadowIntensity}px var(--primary-color),
                            0 0 ${shadowIntensity * 1.5}px var(--primary-color),
                            0 0 ${shadowIntensity * 2}px var(--primary-color)
                        `;
                        closestElement.style.filter = `brightness(${1 + intensity * 0.4})`;
                    }
                }
            }
        });
        
        // Reset effects when leaving navbar
        navbar.addEventListener('mouseleave', () => {
            navLinks.forEach(link => {
                link.style.transform = 'scale(1)';
                link.style.textShadow = 'none';
                link.style.filter = 'brightness(1)';
            });
            
            if (navbarBrand) {
                navbarBrand.style.transform = 'scale(1)';
                navbarBrand.style.textShadow = 'none';
                navbarBrand.style.filter = 'brightness(1)';
            }
        });
    }
});

// Utility functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Optimized scroll handler
const optimizedScrollHandler = debounce(() => {
    // Add any scroll-based effects here
}, 16);

window.addEventListener('scroll', optimizedScrollHandler);
