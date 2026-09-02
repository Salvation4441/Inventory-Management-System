/**
 * Table Export & Refresh Handler for Inventory Management System
 * Handles PDF Export, Excel Export, Print, and Page Refresh on all listing pages.
 */

(function ($) {
  'use strict';

  // Helper: Get Clean Page / Table Title
  function getPageTitle(container) {
    let title = '';
    if (container) {
      const modalTitle = $(container).find('.modal-title, .page-title h4, .page-title h3, h4').first();
      if (modalTitle.length) {
        title = modalTitle.text().trim();
      }
    }
    if (!title) {
      const headerTitle = $('.page-title h4, .page-title h3, .page-title h1, .page-header h4').first();
      if (headerTitle.length) {
        title = headerTitle.text().trim();
      }
    }
    if (!title) {
      title = document.title.split('-')[0].trim() || 'Report';
    }
    return title.replace(/[^\w\s-]/g, '').trim();
  }

  // Helper: Get formatted date string YYYY-MM-DD
  function getFormattedDate() {
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  }

  // Helper: Show brief floating notification
  function showExportToast(message, type = 'success') {
    const toastId = 'export-toast-' + Date.now();
    const iconClass = type === 'success' ? 'ti-check' : 'ti-info-circle';
    const bgClass = type === 'success' ? 'bg-success text-white' : 'bg-primary text-white';

    const toastHtml = `
      <div id="${toastId}" class="position-fixed top-0 end-0 p-3" style="z-index: 99999;">
        <div class="toast show align-items-center ${bgClass} border-0 shadow-lg" role="alert" aria-live="assertive" aria-atomic="true">
          <div class="d-flex align-items-center px-3 py-2">
            <i class="ti ${iconClass} fs-18 me-2"></i>
            <div class="toast-body p-0 fw-medium">
              ${message}
            </div>
            <button type="button" class="btn-close btn-close-white ms-auto me-0" data-bs-dismiss="toast" aria-label="Close"></button>
          </div>
        </div>
      </div>
    `;

    $('body').append(toastHtml);
    setTimeout(function () {
      $(`#${toastId}`).fadeOut('slow', function () {
        $(this).remove();
      });
    }, 3500);
  }

  // Helper: Find target table on the page or inside a context
  function findTargetTable(triggerElement) {
    // If inside a modal, find table in modal
    const modal = $(triggerElement).closest('.modal');
    if (modal.length && modal.find('table').length) {
      return modal.find('table').first();
    }

    // Check closest card or page wrapper
    const card = $(triggerElement).closest('.page-header').siblings('.card, .row');
    if (card.find('table.datatable, table.dataTable, table').length) {
      return card.find('table.datatable, table.dataTable, table').first();
    }

    // Default to main datatable or first table on page
    if ($('table.datatable').length) return $('table.datatable').first();
    if ($('table.dataTable').length) return $('table.dataTable').first();
    if ($('.card table').length) return $('.card table').first();
    if ($('table').length) return $('table').first();

    return null;
  }

  // Extract Clean Table Data (Headers + Rows)
  function extractTableData(tableElement) {
    if (!tableElement || !tableElement.length) return null;

    const $table = $(tableElement);
    const headers = [];
    const colIndices = [];

    // Find headers from thead
    const $thList = $table.find('thead tr').first().find('th, td');
    $thList.each(function (index) {
      const $th = $(this);
      const text = $th.text().replace(/\s+/g, ' ').trim();
      const hasCheckbox = $th.find('input[type="checkbox"]').length > 0;
      const isActionCol = $th.hasClass('action-table-data') || 
                          $th.hasClass('action-table-head') ||
                          text.toLowerCase() === 'action' || 
                          text.toLowerCase() === 'actions' ||
                          ($th.hasClass('no-sort') && !text && !hasCheckbox);

      if (!hasCheckbox && !isActionCol && (text.length > 0 || index > 0)) {
        // Clean header text
        const cleanHeader = text.replace(/[\n\r\t]/g, '').trim() || `Column ${index + 1}`;
        headers.push(cleanHeader);
        colIndices.push(index);
      }
    });

    const rows = [];
    const isDataTable = $.fn.DataTable && $.fn.DataTable.isDataTable($table[0]);

    if (isDataTable) {
      const dt = $table.DataTable();
      // Get all rows matching current search / filter
      const dtRows = dt.rows({ search: 'applied' }).nodes();

      $(dtRows).each(function () {
        const rowData = [];
        const $cells = $(this).find('td');

        colIndices.forEach(function (colIdx) {
          const $cell = $cells.eq(colIdx);
          if ($cell.length) {
            // Clone to avoid modifying DOM
            const $cellClone = $cell.clone();

            // Remove action buttons or dropdowns
            $cellClone.find('.edit-delete-action, .dropdown, .action-table-data, script').remove();

            // Extract clean text
            let cellText = $cellClone.text().replace(/\s+/g, ' ').trim();
            rowData.push(cellText);
          } else {
            rowData.push('');
          }
        });

        if (rowData.some(val => val !== '')) {
          rows.push(rowData);
        }
      });
    } else {
      // Standard HTML table
      $table.find('tbody tr').each(function () {
        // Skip empty table placeholder row
        if ($(this).find('td.dataTables_empty').length) return;

        const rowData = [];
        const $cells = $(this).find('td');

        colIndices.forEach(function (colIdx) {
          const $cell = $cells.eq(colIdx);
          if ($cell.length) {
            const $cellClone = $cell.clone();
            $cellClone.find('.edit-delete-action, .dropdown, .action-table-data, script').remove();
            let cellText = $cellClone.text().replace(/\s+/g, ' ').trim();
            rowData.push(cellText);
          } else {
            rowData.push('');
          }
        });

        if (rowData.some(val => val !== '')) {
          rows.push(rowData);
        }
      });
    }

    return {
      headers: headers,
      rows: rows
    };
  }

  // Export to Excel (.xlsx)
  window.exportTableToExcel = function (triggerElement, customTitle) {
    try {
      const $table = findTargetTable(triggerElement);
      if (!$table || !$table.length) {
        showExportToast('No data table found to export.', 'info');
        return;
      }

      const tableData = extractTableData($table);
      if (!tableData || !tableData.headers.length || !tableData.rows.length) {
        showExportToast('No records available to export.', 'info');
        return;
      }

      const title = customTitle || getPageTitle($(triggerElement).closest('.modal, .content, .page-wrapper'));
      const dateStr = getFormattedDate();
      const fileName = `${title.replace(/\s+/g, '_')}_${dateStr}`;

      if (typeof XLSX === 'undefined') {
        console.error('SheetJS (XLSX) library not loaded.');
        showExportToast('Export library loading failed. Please refresh and try again.', 'info');
        return;
      }

      // Build worksheet array of arrays
      const sheetData = [
        tableData.headers,
        ...tableData.rows
      ];

      const ws = XLSX.utils.aoa_to_sheet(sheetData);

      // Auto-fit column widths
      const colWidths = tableData.headers.map(function (hdr, colIdx) {
        let maxLen = hdr.length;
        tableData.rows.forEach(function (row) {
          const cellVal = (row[colIdx] || '').toString();
          if (cellVal.length > maxLen) {
            maxLen = cellVal.length;
          }
        });
        return { wch: Math.min(Math.max(maxLen + 4, 12), 40) };
      });
      ws['!cols'] = colWidths;

      const wb = XLSX.utils.book_new();
      const sheetName = title.substring(0, 31) || 'Sheet1';
      XLSX.utils.book_append_sheet(wb, ws, sheetName);

      XLSX.writeFile(wb, `${fileName}.xlsx`);
      showExportToast(`Successfully exported ${tableData.rows.length} records to Excel!`, 'success');
    } catch (err) {
      console.error('Error exporting to Excel:', err);
      showExportToast('Error exporting to Excel. Please check console.', 'info');
    }
  };

  // Export to PDF (.pdf)
  window.exportTableToPDF = function (triggerElement, customTitle) {
    try {
      const $table = findTargetTable(triggerElement);
      if (!$table || !$table.length) {
        showExportToast('No data table found to export.', 'info');
        return;
      }

      const tableData = extractTableData($table);
      if (!tableData || !tableData.headers.length || !tableData.rows.length) {
        showExportToast('No records available to export.', 'info');
        return;
      }

      const title = customTitle || getPageTitle($(triggerElement).closest('.modal, .content, .page-wrapper'));
      const dateStr = getFormattedDate();
      const fileName = `${title.replace(/\s+/g, '_')}_${dateStr}`;

      if (!window.jspdf || !window.jspdf.jsPDF) {
        console.error('jsPDF library not loaded.');
        showExportToast('PDF export library loading failed. Please refresh and try again.', 'info');
        return;
      }

      const { jsPDF } = window.jspdf;
      const isLandscape = tableData.headers.length > 5;
      const doc = new jsPDF({
        orientation: isLandscape ? 'landscape' : 'portrait',
        unit: 'pt',
        format: 'a4'
      });

      const pageWidth = doc.internal.pageSize.width;
      const pageHeight = doc.internal.pageSize.height;

      // Header Branding Banner
      doc.setFillColor(254, 159, 67); // Dreams POS Brand Orange
      doc.rect(0, 0, pageWidth, 50, 'F');

      doc.setFont('helvetica', 'bold');
      doc.setFontSize(16);
      doc.setTextColor(255, 255, 255);
      doc.text(title.toUpperCase(), 35, 32);

      doc.setFont('helvetica', 'normal');
      doc.setFontSize(9);
      doc.setTextColor(255, 255, 255);
      const generatedText = `Generated: ${new Date().toLocaleString()} | Total Records: ${tableData.rows.length}`;
      doc.text(generatedText, pageWidth - 35, 32, { align: 'right' });

      // Generate AutoTable
      if (typeof doc.autoTable === 'function') {
        doc.autoTable({
          head: [tableData.headers],
          body: tableData.rows,
          startY: 65,
          theme: 'striped',
          headStyles: {
            fillColor: [33, 37, 41], // Dark header
            textColor: [255, 255, 255],
            fontSize: 8.5,
            fontStyle: 'bold',
            halign: 'left',
            cellPadding: 6
          },
          bodyStyles: {
            fontSize: 8,
            textColor: [40, 40, 40],
            cellPadding: 5
          },
          alternateRowStyles: {
            fillColor: [248, 249, 250]
          },
          margin: { top: 65, left: 35, right: 35, bottom: 35 },
          didDrawPage: function (data) {
            // Footer
            doc.setFontSize(8);
            doc.setTextColor(130, 130, 130);
            doc.text(
              `Dreams POS - Inventory Management System`,
              35,
              pageHeight - 15
            );
            const pageNumber = `Page ${data.pageNumber} of ${doc.internal.getNumberOfPages()}`;
            doc.text(pageNumber, pageWidth - 35, pageHeight - 15, { align: 'right' });
          }
        });

        doc.save(`${fileName}.pdf`);
        showExportToast(`Successfully exported ${tableData.rows.length} records to PDF!`, 'success');
      } else {
        console.error('jsPDF AutoTable plugin not available.');
        showExportToast('PDF AutoTable plugin not loaded.', 'info');
      }
    } catch (err) {
      console.error('Error exporting to PDF:', err);
      showExportToast('Error exporting to PDF. Please check console.', 'info');
    }
  };

  // Global Event Handlers
  $(document).ready(function () {
    // 1. PDF Export Click Handler
    $(document).on(
      'click',
      '.table-top-head a[title*="Pdf"], .table-top-head a[title*="PDF"], .table-top-head a[data-bs-original-title*="Pdf"], .table-top-head a[data-bs-original-title*="PDF"], .table-top-head a:has(img[src*="pdf"]), .btn-export-pdf',
      function (e) {
        e.preventDefault();
        window.exportTableToPDF(this);
      }
    );

    // 2. Excel Export Click Handler
    $(document).on(
      'click',
      '.table-top-head a[title*="Excel"], .table-top-head a[data-bs-original-title*="Excel"], .table-top-head a:has(img[src*="excel"]), .btn-export-excel',
      function (e) {
        e.preventDefault();
        window.exportTableToExcel(this);
      }
    );

    // 3. Refresh Click Handler
    $(document).on(
      'click',
      '.table-top-head a[title*="Refresh"], .table-top-head a[data-bs-original-title*="Refresh"], .table-top-head a:has(.ti-refresh), .btn-refresh, .btn-refresh-list',
      function (e) {
        e.preventDefault();
        const $icon = $(this).find('i.ti-refresh, .ti-refresh');
        if ($icon.length) {
          $icon.addClass('fa-spin').css({
            'animation': 'spin 0.8s linear infinite',
            'display': 'inline-block'
          });
        }
        setTimeout(function () {
          window.location.reload();
        }, 150);
      }
    );

    // 4. Print Click Handler
    $(document).on(
      'click',
      '.table-top-head a[title*="Print"], .table-top-head a[data-bs-original-title*="Print"], .table-top-head a:has(img[src*="printer"]), .table-top-head a:has(.ti-printer), .printimg',
      function (e) {
        e.preventDefault();
        window.print();
      }
    );

    // Ensure all table-top-head links have href="javascript:void(0);" and cursor pointer
    $('.table-top-head a').each(function () {
      const $a = $(this);
      if (!$a.attr('href') || $a.attr('href') === '#') {
        $a.attr('href', 'javascript:void(0);');
      }
      $a.css('cursor', 'pointer');
    });
  });

})(jQuery);
