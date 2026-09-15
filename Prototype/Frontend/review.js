let editableCompliance = null;

function statusLabel(status) {
  return status === 'PASS'
    ? 'Pass'
    : status === 'FAIL'
      ? 'Fail'
      : status === 'SKIPPED'
        ? 'Skipped'
        : 'Manual review';
}

function refreshEditableSummary() {
  if (!editableCompliance) return;

  const results = editableCompliance.results || [];
  const activeResults = results.filter(rule => rule.status !== 'SKIPPED');
  const passed = activeResults.filter(rule => rule.status === 'PASS').length;
  const failed = activeResults.filter(rule => rule.status === 'FAIL').length;
  const manualReview = activeResults.length - passed - failed;
  const skipped = results.length - activeResults.length;
  const score = activeResults.length
    ? Math.round(((passed + (manualReview * 0.7)) / activeResults.length) * 100)
    : 0;
  const overallStatus = failed === 0 && manualReview === 0
    ? activeResults.length ? 'COMPLIANT' : 'NEEDS REVIEW'
    : passed === 0 && manualReview === 0
      ? 'NON-COMPLIANT'
      : 'NEEDS REVIEW';

  editableCompliance.passed = passed;
  editableCompliance.failed = failed;
  editableCompliance.manual_review = manualReview;
  editableCompliance.skipped = skipped;
  editableCompliance.score = score;
  editableCompliance.overall_status = overallStatus;

  $('overallStatus').textContent = normalizeStatus(overallStatus);
  $('complianceScore').textContent = `${score}%`;
  $('scoreProgress').style.width = `${score}%`;
  $('passedCount').textContent = passed;
  $('manualCount').textContent = manualReview;
  $('resultHeadline').textContent = overallStatus === 'COMPLIANT'
    ? 'Package appears compliant'
    : overallStatus === 'NON-COMPLIANT'
      ? 'Issues were found'
      : 'Manual review recommended';
  $('resultIcon').textContent = overallStatus === 'COMPLIANT' ? '✓' : overallStatus === 'NON-COMPLIANT' ? '!' : '?';
  $('resultBanner').className = `result-banner status-${statusClass(overallStatus)}`;
  renderIssues(results);
}

window.renderRules = function renderEditableRules(items) {
  const bannerClass = $('resultBanner').className;
  editableCompliance = window.currentCompliance || {
    overall_status: bannerClass.includes('status-pass')
      ? 'COMPLIANT'
      : bannerClass.includes('status-fail')
        ? 'NON-COMPLIANT'
        : 'NEEDS REVIEW',
    score: Number.parseFloat($('complianceScore').textContent) || 0,
    results: items
  };
  editableCompliance.results = items;
  window.currentCompliance = editableCompliance;

  const body = $('ruleTableBody');
  body.innerHTML = items.map((rule, index) => `<tr>
    <td><strong>${esc(rule.field || 'Requirement')}</strong></td>
    <td>${esc(rule.description || '')}${rule.resolution ? `<small class="rule-resolution">${esc(rule.resolution)}</small>` : ''}</td>
    <td><select class="rule-status-select" data-rule-index="${index}" aria-label="Status for ${esc(rule.field || 'requirement')}">
      ${['PASS', 'FAIL', 'MANUAL REVIEW', 'SKIPPED'].map(status => `<option value="${status}" ${rule.status === status ? 'selected' : ''}>${statusLabel(status)}</option>`).join('')}
    </select></td>
  </tr>`).join('');

  body.querySelectorAll('.rule-status-select').forEach(select => {
    select.addEventListener('change', event => {
      editableCompliance.results[Number(event.target.dataset.ruleIndex)].status = event.target.value;
      refreshEditableSummary();
    });
  });
};

window.generateReportForScan = async function generateEditableReport(s, endpoint, filename) {
  try {
    const compliance = window.currentCompliance || {
      overall_status: s.overall_status,
      score: s.compliance_score,
      results: []
    };
    const payload = {
      scan_id: s.scan_id,
      product_name: s.product_name,
      product_type: s.product_type,
      package_type: s.package_type,
      extracted_text: s.extracted_text,
      readability: s.readability || {
        status: s.readability_status,
        average_confidence: s.readability_confidence
      },
      compliance
    };
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(payload)
    });
    if (!response.ok) {
      let error = {};
      try { error = await response.json(); } catch {}
      throw new Error(error.error || 'Report generation failed.');
    }
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.click();
    URL.revokeObjectURL(url);
    toast('Report downloaded with your final statuses');
  } catch (error) {
    toast(error.message);
  }
};
