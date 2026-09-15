const inspectionSteps = [...document.querySelectorAll('.progress-steps .step')];
const loadingPanel = document.getElementById('loadingPanel');
const resultSection = document.getElementById('resultSection');
const scanButton = document.getElementById('scanButton');
const newScanButton = document.getElementById('newScanButton');

function setInspectionStep(activeIndex) {
  inspectionSteps.forEach((step, index) => {
    step.classList.toggle('active', index === activeIndex);
    step.classList.toggle('completed', index < activeIndex);
  });
}

if (inspectionSteps.length) {
  setInspectionStep(0);

  new MutationObserver(() => {
    if (!loadingPanel?.classList.contains('hidden')) {
      setInspectionStep(1);
    } else if (!resultSection?.classList.contains('hidden')) {
      setInspectionStep(2);
    }
  }).observe(document.getElementById('scan'), {
    subtree: true,
    attributes: true,
    attributeFilter: ['class']
  });

  scanButton?.addEventListener('click', () => setInspectionStep(1));
  newScanButton?.addEventListener('click', () => setInspectionStep(0));
}
