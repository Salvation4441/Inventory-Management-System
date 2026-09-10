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

  // =========================================================================
  // 4. Image Resolution Guard: Hides any image that does not resolve
  // =========================================================================
  function initImageResolutionGuard() {
    function hideIfUnresolved(img) {
      if (!img || img.nodeType !== Node.ELEMENT_NODE || img.tagName !== 'IMG') return;
      if (img.getAttribute('data-img-unresolved') === 'true') return;

      const rawSrc = img.getAttribute('src');
      const src = (rawSrc || '').trim();

      // Detect empty, missing, or unresolvable placeholder paths
      if (
        !src ||
        src === '#' ||
        src === 'about:blank' ||
        src === 'undefined' ||
        src === 'null' ||
        src === 'None' ||
        src.endsWith('/None') ||
        src.endsWith('/media/')
      ) {
        img.style.display = 'none';
        img.classList.add('img-unresolved');
        img.setAttribute('data-img-unresolved', 'true');
        return;
      }

      // If already finished loading with 0 dimensions, it failed to resolve
      if (img.complete) {
        if (img.naturalWidth === 0 || img.naturalHeight === 0) {
          img.style.display = 'none';
          img.classList.add('img-unresolved');
          img.setAttribute('data-img-unresolved', 'true');
        }
      } else {
        img.addEventListener('error', function onImgErr() {
          img.style.display = 'none';
          img.classList.add('img-unresolved');
          img.setAttribute('data-img-unresolved', 'true');
          img.removeEventListener('error', onImgErr);
        });
      }
    }

    // Audit all existing images
    document.querySelectorAll('img').forEach(hideIfUnresolved);

    // Global capture listener for any future or dynamic image error event
    window.addEventListener('error', function (e) {
      if (e.target && e.target.tagName === 'IMG') {
        hideIfUnresolved(e.target);
      }
    }, true);

    // MutationObserver to catch dynamically added images (e.g. modals, tables, POS, reports)
    if (window.MutationObserver) {
      const observer = new MutationObserver(function (mutations) {
        mutations.forEach(function (mutation) {
          mutation.addedNodes.forEach(function (node) {
            if (node.nodeType === Node.ELEMENT_NODE) {
              if (node.tagName === 'IMG') {
                hideIfUnresolved(node);
              } else if (node.querySelectorAll) {
                node.querySelectorAll('img').forEach(hideIfUnresolved);
              }
              if (node.tagName === 'TABLE' || (node.querySelectorAll && node.querySelector('table, td'))) {
                sanitizeTableCells(node);
              }
            }
          });
        });
      });
      observer.observe(document.documentElement || document.body, { childList: true, subtree: true });
    }
  }

  // =========================================================================
  // Automatic Table Cell Sanitizer (Eliminates literal "None", "null", "undefined")
  // =========================================================================
  function sanitizeTableCells(root) {
    try {
      const context = root || document;
      const cells = context.querySelectorAll ? context.querySelectorAll('table tbody td') : [];
      cells.forEach(function (td) {
        if (td.querySelector('input, select, img, button, a.avatar, .edit-delete-action, .checkboxs')) return;
        const text = td.textContent.trim();
        if (text === 'None' || text === 'none' || text === 'null' || text === 'undefined') {
          td.innerHTML = '<span class="text-muted">-</span>';
        }
      });
    } catch (e) {}
  }

  // =========================================================================
  // 5. Professional Table Checkbox Manager
  // =========================================================================
  function initTableCheckboxes() {
    let lastCheckedRowCheckbox = null;
    let activeTable = null;

    function getTableFromTarget($el) {
      return $el.closest('table');
    }

    function updateMasterCheckboxState($table) {
      if (!$table || !$table.length) return;
      const $master = $table.find('thead input[type="checkbox"], #select-all, #select-all2, .select-all');
      const $visibleCheckboxes = $table.find('tbody tr:visible input[type="checkbox"]');
      const totalVisible = $visibleCheckboxes.length;
      const checkedVisible = $visibleCheckboxes.filter(':checked').length;

      if (totalVisible > 0 && checkedVisible === totalVisible) {
        $master.prop('checked', true);
        $master.prop('indeterminate', false);
      } else if (checkedVisible > 0) {
        $master.prop('checked', false);
        $master.prop('indeterminate', true);
      } else {
        $master.prop('checked', false);
        $master.prop('indeterminate', false);
      }

      // Update row visual highlight
      $visibleCheckboxes.each(function () {
        $(this).closest('tr').toggleClass('selected-row', this.checked);
      });

      updateBulkActionBar($table);
    }

    function updateBulkActionBar($table) {
      activeTable = $table;
      const $allChecked = $('table').find('tbody input[type="checkbox"]:checked');
      const totalChecked = $allChecked.length;
      const $bar = $('#table-bulk-actions');

      if (!$bar.length) return;

      if (totalChecked > 0) {
        $('#bulk-selected-count').text(`${totalChecked} ${totalChecked === 1 ? 'item' : 'items'} selected`);
        $bar.show();
        requestAnimationFrame(() => $bar.addClass('show'));
      } else {
        $bar.removeClass('show');
        setTimeout(() => {
          if (!$('#table-bulk-actions').hasClass('show')) {
            $bar.hide();
          }
        }, 350);
      }
    }

    // A. Master "Select All" click
    $(document).on('click', 'thead input[type="checkbox"], #select-all, #select-all2, .select-all', function (e) {
      const $master = $(this);
      const $table = getTableFromTarget($master);
      if (!$table.length) return;

      const isChecked = $master.prop('checked');
      // Only toggle visible rows in this specific table (honoring active page & filters)
      const $rowCheckboxes = $table.find('tbody tr:visible input[type="checkbox"]');
      $rowCheckboxes.prop('checked', isChecked);
      $rowCheckboxes.closest('tr').toggleClass('selected-row', isChecked);

      $master.prop('indeterminate', false);
      updateBulkActionBar($table);
    });

    // B. Individual row checkbox click & Shift + Click range selection
    $(document).on('click', 'tbody input[type="checkbox"]', function (e) {
      const $current = $(this);
      const $table = getTableFromTarget($current);
      const isChecked = $current.prop('checked');

      $current.closest('tr').toggleClass('selected-row', isChecked);

      // Shift + Click Range Selection
      if (e.shiftKey && lastCheckedRowCheckbox && lastCheckedRowCheckbox.length) {
        const $lastTable = getTableFromTarget(lastCheckedRowCheckbox);
        if ($lastTable.length && $table.length && $lastTable[0] === $table[0]) {
          const $visible = $table.find('tbody tr:visible input[type="checkbox"]');
          const startIndex = $visible.index(lastCheckedRowCheckbox);
          const endIndex = $visible.index($current);
          if (startIndex !== -1 && endIndex !== -1) {
            const min = Math.min(startIndex, endIndex);
            const max = Math.max(startIndex, endIndex);
            $visible.slice(min, max + 1).each(function () {
              $(this).prop('checked', isChecked);
              $(this).closest('tr').toggleClass('selected-row', isChecked);
            });
          }
        }
      }

      lastCheckedRowCheckbox = $current;
      updateMasterCheckboxState($table);
    });

    // C. Bulk Action Buttons Handlers
    $(document).on('click', '#bulk-deselect-btn, #bulk-close-btn', function () {
      $('table tbody input[type="checkbox"]:checked').prop('checked', false);
      $('table tr.selected-row').removeClass('selected-row');
      $('table thead input[type="checkbox"], #select-all, #select-all2, .select-all')
        .prop('checked', false)
        .prop('indeterminate', false);
      $('#table-bulk-actions').removeClass('show');
      setTimeout(() => $('#table-bulk-actions').hide(), 350);
      window.showMotionToast('Selection cleared', 'info', 2000);
    });

    $(document).on('click', '#bulk-excel-btn', function () {
      const $targetTable = activeTable && activeTable.length ? activeTable : $('table.datatable, table.table').first();
      if (typeof window.exportTableToExcel === 'function') {
        window.exportTableToExcel($targetTable, null, true);
      } else {
        window.showMotionToast('Excel export handler not available', 'warning', 2500);
      }
    });

    $(document).on('click', '#bulk-pdf-btn', function () {
      const $targetTable = activeTable && activeTable.length ? activeTable : $('table.datatable, table.table').first();
      if (typeof window.exportTableToPDF === 'function') {
        window.exportTableToPDF($targetTable, null, true);
      } else {
        window.showMotionToast('PDF export handler not available', 'warning', 2500);
      }
    });

    $(document).on('click', '#bulk-print-btn', function () {
      const $targetTable = activeTable && activeTable.length ? activeTable : $('table.datatable, table.table').first();
      if (typeof window.printSelectedRows === 'function') {
        window.printSelectedRows($targetTable);
      } else {
        window.print();
      }
    });

    // D. DataTables Draw / Redraw Event Sync
    $(document).on('draw.dt', function (e, settings) {
      try {
        const tableApi = new $.fn.dataTable.Api(settings);
        const $table = $(tableApi.table().node());
        updateMasterCheckboxState($table);
        if ($table && $table.length) {
          sanitizeTableCells($table[0]);
        }
      } catch (err) {}
    });
  }

  // Self-initialize on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () {
      initImageResolutionGuard();
      sanitizeTableCells(document);
      initTableCheckboxes();
    });
  } else {
    initImageResolutionGuard();
    sanitizeTableCells(document);
    initTableCheckboxes();
  }

})(window, document, window.jQuery || window.$);
