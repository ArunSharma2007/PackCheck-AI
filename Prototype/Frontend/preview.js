const scannerShell = document.querySelector('.scanner-shell');
const imagePreview = document.getElementById('imagePreview');

function updatePreviewLayout() {
  scannerShell?.classList.toggle(
    'preview-active',
    Boolean(imagePreview && !imagePreview.classList.contains('hidden'))
  );
}

if (scannerShell && imagePreview) {
  new MutationObserver(updatePreviewLayout).observe(imagePreview, {
    attributes: true,
    attributeFilter: ['class', 'src']
  });
  imagePreview.addEventListener('load', updatePreviewLayout);
  updatePreviewLayout();
}
