/**
 * UI Motion & Micro-Interactions Engine
 * Eliminates unnecessary page reloads with smooth sliding, morphing, and glassmorphic toast feedback.
 */

(function (window, document, $) {
  'use strict';

  // 1. Toast Notification System
  function ensureToastContainer() {
    let container = document.getElementById('glass-toast-container');
    if (!container) {
      container = document.createElement('div');
      container.id = 'glass-toast-container';
      container.className = 'glass-toast-container';
      document.body.appendChild(container);
    }
    return container;
  }

  function getToastIcon(type) {
    switch (type) {
      case 'danger':
      case 'error':
        return '<i class="ti ti-alert-circle"></i>';
      case 'warning':
        return '<i class="ti ti-alert-triangle"></i>';
      case 'info':
        return '<i class="ti ti-info-circle"></i>';
      case 'success':
      default:
        return '<i class="ti ti-check"></i>';
    }
  }

  window.showMotionToast = function (message, type = 'success', duration = 3500) {
    const container = ensureToastContainer();
    const toast = document.createElement('div');
    const safeType = type === 'error' ? 'danger' : type;
    toast.className = `glass-toast glass-toast-${safeType}`;

    const iconHtml = getToastIcon(safeType);

    toast.innerHTML = `
      <div class="glass-toast-icon">${iconHtml}</div>
      <div class="glass-toast-content">${message}</div>
      <button type="button" class="glass-toast-close" aria-label="Close">
        <i class="ti ti-x"></i>
      </button>
      <div class="glass-toast-progress" style="animation-duration: ${duration}ms;"></div>
    `;

    container.appendChild(toast);

    // Trigger enter animation on next frame
    requestAnimationFrame(() => {
      toast.classList.add('glass-toast-show');
    });

    let autoDismissTimer = setTimeout(() => {
      dismissToast(toast);
    }, duration);

    const closeBtn = toast.querySelector('.glass-toast-close');
    if (closeBtn) {
      closeBtn.addEventListener('click', () => {
        clearTimeout(autoDismissTimer);
        dismissToast(toast);
      });
    }

    function dismissToast(targetToast) {
      targetToast.classList.remove('glass-toast-show');
      targetToast.classList.add('glass-toast-hide');
      setTimeout(() => {
        if (targetToast.parentNode) {
          targetToast.parentNode.removeChild(targetToast);
        }
      }, 350);
    }
  };

  // 2. Smooth Sliding Row Deletion
  window.animateRowRemoval = function (rowElement, dataTableInstance, onComplete) {
    if (!rowElement) return;

    const $row = $(rowElement);
    
    // Add sliding exit animation
    $row.addClass('row-slide-exit');

    setTimeout(() => {
      $row.addClass('row-collapse-exit');

      setTimeout(() => {
        if (dataTableInstance && typeof dataTableInstance.row === 'function') {
          try {
            dataTableInstance.row($row).remove().draw(false);
          } catch (e) {
            $row.remove();
          }
        } else if ($.fn.DataTable && $.fn.DataTable.isDataTable($row.closest('table'))) {
          try {
            $row.closest('table').DataTable().row($row).remove().draw(false);
          } catch (e) {
            $row.remove();
          }
        } else {
          $row.remove();
        }

        if (typeof onComplete === 'function') {
          onComplete();
        }
      }, 300);
    }, 280);
  };

  // 3. Smooth Table Morph & Refresh
  window.morphRefreshTable = function (tableSelector, dtInstance) {
    const $table = $(tableSelector || '.datatable, table.table');
    const $container = $table.closest('.table-responsive, .card-body');
    
    $container.addClass('table-morph-refresh table-morph-active');

    // Reset DataTables search & column filters
    try {
      const table = dtInstance || ($table.length && $.fn.DataTable && $.fn.DataTable.isDataTable($table[0]) ? $table.DataTable() : null);
      if (table) {
        table.search('').columns().search('').draw();
      }
      // Also clear custom search inputs
      $('.search-input input, .dataTables_filter input').val('');
    } catch (err) {
      console.warn('Table filter reset notice:', err);
    }

    setTimeout(() => {
      $container.removeClass('table-morph-active');
      window.showMotionToast('Table view refreshed without reloading', 'success', 2500);
    }, 300);
  };

})(window, document, window.jQuery || window.$);
