document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('releases-form');
    if (!form) return;

    const checkboxes = form.querySelectorAll('.release-check');
    const checkAll = document.getElementById('check-all');
    const selectAllBtn = document.getElementById('select-all');
    const deselectAllBtn = document.getElementById('deselect-all');
    const previewBtn = document.getElementById('preview-btn');
    const releasesDataInput = document.getElementById('releases-data');
    const selectionCount = document.getElementById('selection-count');

    function updateState() {
        const checked = form.querySelectorAll('.release-check:checked');
        const count = checked.length;

        if (selectionCount) {
            selectionCount.textContent = count + ' selected';
        }

        if (previewBtn) {
            previewBtn.disabled = false;
        }

        if (checkAll) {
            checkAll.checked = count === checkboxes.length && count > 0;
            checkAll.indeterminate = count > 0 && count < checkboxes.length;
        }
    }

    function collectSelectedReleases() {
        const selected = [];
        form.querySelectorAll('.release-check:checked').forEach(function (cb) {
            try {
                selected.push(JSON.parse(cb.dataset.release));
            } catch (e) {
                // skip invalid data
            }
        });
        return selected;
    }

    // Individual checkbox changes
    checkboxes.forEach(function (cb) {
        cb.addEventListener('change', function () {
            updateState();
            hideWarning();
        });
    });

    // Check all header checkbox
    if (checkAll) {
        checkAll.addEventListener('change', function () {
            checkboxes.forEach(function (cb) {
                cb.checked = checkAll.checked;
            });
            updateState();
        });
    }

    // Select All button
    if (selectAllBtn) {
        selectAllBtn.addEventListener('click', function () {
            checkboxes.forEach(function (cb) {
                cb.checked = true;
            });
            updateState();
        });
    }

    // Deselect All button
    if (deselectAllBtn) {
        deselectAllBtn.addEventListener('click', function () {
            checkboxes.forEach(function (cb) {
                cb.checked = false;
            });
            updateState();
        });
    }

    // Show or hide inline warning message
    function showWarning(message) {
        var warning = document.getElementById('selection-warning');
        if (!warning) {
            warning = document.createElement('div');
            warning.id = 'selection-warning';
            warning.className = 'alert alert-warning';
            var controls = document.querySelector('.selection-controls');
            if (controls) {
                controls.parentNode.insertBefore(warning, controls.nextSibling);
            }
        }
        warning.textContent = message;
        warning.style.display = 'block';
    }

    function hideWarning() {
        var warning = document.getElementById('selection-warning');
        if (warning) {
            warning.style.display = 'none';
        }
    }

    // Form submission: collect selected releases into hidden field
    form.addEventListener('submit', function (e) {
        var selected = collectSelectedReleases();
        if (selected.length === 0) {
            e.preventDefault();
            showWarning('Please select at least one release before previewing.');
            return;
        }
        hideWarning();
        if (releasesDataInput) {
            releasesDataInput.value = JSON.stringify(selected);
        }
    });

    // Initial state
    updateState();
});
