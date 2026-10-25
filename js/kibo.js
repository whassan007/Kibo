/**
 * KIBO.IS — Production Core JavaScript Engine
 * Features: Dark/Light Mode Theme Toggle, Mobile Nav, FAQ Accordion, Cookie Consent Gate, UTM Attribution, Analytics
 */

(function () {
  'use strict';

  // --------------------------------------------------------------------------
  // 1. Dark Mode & Light Mode Theme Handler
  // --------------------------------------------------------------------------
  function initThemeEngine() {
    const themeKey = 'kibo_theme';
    const storedTheme = localStorage.getItem(themeKey) || 'dark'; // Default to dark mode first

    document.documentElement.setAttribute('data-theme', storedTheme);
    updateThemeToggleIcons(storedTheme);

    document.querySelectorAll('.theme-toggle-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const currentTheme = document.documentElement.getAttribute('data-theme') || 'dark';
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem(themeKey, newTheme);
        updateThemeToggleIcons(newTheme);

        console.log(`[KIBO Theme Switch]: Changed to ${newTheme} mode`);
      });
    });
  }

  function updateThemeToggleIcons(theme) {
    document.querySelectorAll('.theme-toggle-btn').forEach(btn => {
      btn.innerHTML = theme === 'dark' ? '☀️' : '🌙';
      btn.setAttribute('aria-label', `Switch to ${theme === 'dark' ? 'Light' : 'Dark'} Mode`);
      btn.setAttribute('title', `Switch to ${theme === 'dark' ? 'Light' : 'Dark'} Mode`);
    });
  }

  // --------------------------------------------------------------------------
  // 2. UTM Parameter & Campaign Attribution Preservation
  // --------------------------------------------------------------------------
  function captureUTMParameters() {
    const urlParams = new URLSearchParams(window.location.search);
    const utmKeys = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term'];
    let attributionData = JSON.parse(localStorage.getItem('kibo_utm_attribution') || '{}');

    let updated = false;
    utmKeys.forEach(key => {
      if (urlParams.has(key)) {
        attributionData[key] = urlParams.get(key);
        updated = true;
      }
    });

    if (urlParams.has('ref')) {
      attributionData['referrer'] = urlParams.get('ref');
      updated = true;
    } else if (document.referrer && !document.referrer.includes(window.location.hostname)) {
      attributionData['referrer'] = document.referrer;
      updated = true;
    }

    if (updated) {
      localStorage.setItem('kibo_utm_attribution', JSON.stringify(attributionData));
    }

    // Attach UTM parameters to internal links
    document.querySelectorAll('a[href*="signup"], a[href*="login"], a[href*="contact"]').forEach(link => {
      try {
        const linkUrl = new URL(link.href, window.location.origin);
        Object.keys(attributionData).forEach(key => {
          if (!linkUrl.searchParams.has(key)) {
            linkUrl.searchParams.set(key, attributionData[key]);
          }
        });
        link.href = linkUrl.toString();
      } catch (e) {}
    });
  }

  // --------------------------------------------------------------------------
  // 3. Mobile Navigation Toggle
  // --------------------------------------------------------------------------
  function initMobileMenu() {
    const toggleBtn = document.querySelector('.mobile-toggle');
    const navMenu = document.querySelector('.nav-menu');

    if (toggleBtn && navMenu) {
      toggleBtn.addEventListener('click', () => {
        const expanded = toggleBtn.getAttribute('aria-expanded') === 'true' || false;
        toggleBtn.setAttribute('aria-expanded', !expanded);
        navMenu.classList.toggle('active');
      });

      document.addEventListener('click', (e) => {
        if (!toggleBtn.contains(e.target) && !navMenu.contains(e.target)) {
          navMenu.classList.remove('active');
          toggleBtn.setAttribute('aria-expanded', 'false');
        }
      });
    }
  }

  // --------------------------------------------------------------------------
  // 4. FAQ Accordion Handler
  // --------------------------------------------------------------------------
  function initFAQ() {
    const faqItems = document.querySelectorAll('.faq-item');

    faqItems.forEach(item => {
      const questionBtn = item.querySelector('.faq-question');
      if (questionBtn) {
        questionBtn.addEventListener('click', () => {
          const isActive = item.classList.contains('active');
          
          faqItems.forEach(i => {
            i.classList.remove('active');
            const btn = i.querySelector('.faq-question');
            if (btn) btn.setAttribute('aria-expanded', 'false');
          });

          if (!isActive) {
            item.classList.add('active');
            questionBtn.setAttribute('aria-expanded', 'true');
          }
        });
      }
    });
  }

  // --------------------------------------------------------------------------
  // 5. Privacy & Cookie Consent Banner Gate
  // --------------------------------------------------------------------------
  function initCookieConsent() {
    const consentKey = 'kibo_cookie_consent';
    const banner = document.getElementById('cookie-banner');
    const acceptBtn = document.getElementById('cookie-accept');
    const rejectBtn = document.getElementById('cookie-reject');

    const storedConsent = localStorage.getItem(consentKey);

    if (!storedConsent && banner) {
      banner.classList.add('active');
    } else if (storedConsent === 'accepted') {
      enableAnalytics();
    }

    if (acceptBtn) {
      acceptBtn.addEventListener('click', () => {
        localStorage.setItem(consentKey, 'accepted');
        if (banner) banner.classList.remove('active');
        enableAnalytics();
      });
    }

    if (rejectBtn) {
      rejectBtn.addEventListener('click', () => {
        localStorage.setItem(consentKey, 'rejected');
        if (banner) banner.classList.remove('active');
      });
    }
  }

  function enableAnalytics() {
    if (!window.plausibleLoaded) {
      const script = document.createElement('script');
      script.defer = true;
      script.dataset.domain = 'kibo.is';
      script.src = 'https://plausible.io/js/script.js';
      document.head.appendChild(script);
      window.plausibleLoaded = true;
    }
  }

  window.trackConversion = function (eventName, metadata) {
    console.log(`[KIBO Analytics Event]: ${eventName}`, metadata || {});
    if (window.plausible) {
      window.plausible(eventName, { props: metadata || {} });
    }
  };

  // --------------------------------------------------------------------------
  // 6. Initialize Engine on DOM Content Loaded
  // --------------------------------------------------------------------------
  document.addEventListener('DOMContentLoaded', () => {
    initThemeEngine();
    captureUTMParameters();
    initMobileMenu();
    initFAQ();
    initCookieConsent();

    document.querySelectorAll('.btn-primary, .btn-gradient').forEach(button => {
      button.addEventListener('click', () => {
        const ctaText = button.textContent.trim();
        window.trackConversion('CTA_Click', { label: ctaText, page: window.location.pathname });
      });
    });
  });
})();
