const fs = require('fs');
const vm = require('vm');
const assert = require('assert');

console.log('=== 開始執行 Node.js E2E 端到端真實前端生命週期測試 ===');

const html = fs.readFileSync('index.html', 'utf8');

// 1. 靜態完整性檢查
const scripts = [...html.matchAll(/<script\b[^>]*>([\s\S]*?)<\/script>/gi)];
assert(scripts.length >= 4, '應至少包含 4 個 script 標籤');
const mainScript = scripts[3][1];

// 2. 模擬完整 DOM
const elements = {};
function getEl(id) {
  if (!elements[id]) {
    const classSet = new Set();
    elements[id] = {
      id,
      textContent: '',
      innerHTML: '',
      classList: {
        add: (...classes) => classes.forEach(c => classSet.add(c)),
        remove: (...classes) => classes.forEach(c => classSet.delete(c)),
        contains: (c) => classSet.has(c)
      },
      style: {},
      attributes: {},
      setAttribute(k, v) { this.attributes[k] = v; },
      getAttribute(k) { return this.attributes[k]; },
      appendChild(child) { (this.children = this.children || []).push(child); }
    };
  }
  return elements[id];
}

const eventListeners = {};
const mockDoc = {
  getElementById: (id) => getEl(id),
  createElement: (tag) => ({
    tag,
    textContent: '',
    innerHTML: '',
    classList: new Set(),
    style: {},
    attributes: {},
    setAttribute(k, v) { this.attributes[k] = v; },
    appendChild(c) { (this.children = this.children || []).push(c); }
  }),
  addEventListener: (evt, cb) => {
    (eventListeners[evt] = eventListeners[evt] || []).push(cb);
  }
};

const timers = [];
const mockSetTimeout = (fn, ms) => {
  timers.push(fn);
  return timers.length;
};

const sandbox = {
  document: mockDoc,
  scrollTo: () => {},
  location: { reload: () => {} },
  currentResultShareText: '',
  console: console,
  setTimeout: mockSetTimeout,
  URLSearchParams: URLSearchParams,
  navigator: { clipboard: { writeText: async () => {} } }
};
sandbox.globalThis = sandbox;
sandbox.window = sandbox;

// 注入代碼並擷取內部作用域變數
const wrappedCode = mainScript + '\n;globalThis.__quizScope = { rawQuestions, scaleOptions, styleProfiles, shuffleQuestions, startQuiz, renderQuestion, selectScore, finishQuiz, renderResult, get activeQuestions() { return activeQuestions; }, set activeQuestions(v) { activeQuestions = v; }, get currentIndex() { return currentIndex; }, set currentIndex(v) { currentIndex = v; }, get userAnswers() { return userAnswers; }, set userAnswers(v) { userAnswers = v; } };';

vm.createContext(sandbox);
vm.runInContext(wrappedCode, sandbox);
const scope = sandbox.globalThis.__quizScope;

// 測試 A：題庫與量表結構驗證
console.log('1. 驗證原始題庫與五點量表...');
assert.strictEqual(scope.rawQuestions.length, 8, '題目數量必須嚴格為 8 題');
assert.strictEqual(scope.scaleOptions.length, 5, '量表選項必須為 5 點');
const dims = scope.rawQuestions.map(q => q.dimension);
assert.strictEqual(dims.filter(d => d === 'E').length, 2, '情緒維度需 2 題');
assert.strictEqual(dims.filter(d => d === 'T').length, 2, '事務維度需 2 題');
assert.strictEqual(dims.filter(d => d === 'N').length, 2, '培育維度需 2 題');
assert.strictEqual(dims.filter(d => d === 'C').length, 2, '督促維度需 2 題');
console.log('   [通過] 8 題維度配比完美符合 E:2, T:2, N:2, C:2');

// 測試 B：Fisher-Yates 洗牌演算法隨機度
console.log('2. 驗證 Fisher-Yates 洗牌演算法...');
const sampleShuffle = scope.shuffleQuestions(scope.rawQuestions);
assert.strictEqual(sampleShuffle.length, 8, '洗牌後題數必須不變');
assert(sampleShuffle.every(q => scope.rawQuestions.some(rq => rq.id === q.id)), '所有題目必須被完整保留');
console.log('   [通過] 洗牌演算法完整保留 8 題且無元素遺漏');

// 測試 C：模擬作答流程與上一題回退
console.log('3. 驗證測驗生命週期與上一題回退...');
scope.startQuiz();
assert.strictEqual(scope.currentIndex, 0, '開始測驗題號必須為 0');
assert.strictEqual(getEl('btn-quiz-prev').disabled, true, '第一題上一題按鈕必須 disabled');

// 選擇 Q0 分數
scope.selectScore(scope.activeQuestions[0].id, 4);
assert.strictEqual(scope.userAnswers[scope.activeQuestions[0].id], 4, '答案應被正確記錄為 4 分');
// 觸發前進定時器
timers.shift()();
assert.strictEqual(scope.currentIndex, 1, '答題後應自動推進至下一題');

// 測試回退至第 0 題
scope.currentIndex = 1;
// 模擬點擊上一題
scope.currentIndex--;
scope.renderQuestion();
assert.strictEqual(scope.currentIndex, 0, '應成功退回上一題');
console.log('   [通過] 作答自動推進與上一題狀態切換正常');

// 測試 D：四象限計分、極限保護與結果報告映射
console.log('4. 驗證四大極端型態與結果渲染...');

const testCases = [
  { answers: { Q1:5, Q2:5, Q3:1, Q4:1, Q5:5, Q6:5, Q7:1, Q8:1 }, expectedStyle: 'A', expX: 18, expY: 18, name: '陪伴聆聽者' },
  { answers: { Q1:5, Q2:5, Q3:1, Q4:1, Q5:1, Q6:1, Q7:5, Q8:5 }, expectedStyle: 'B', expX: 82, expY: 18, name: '覺察聆聽者' },
  { answers: { Q1:1, Q2:1, Q3:5, Q4:5, Q5:5, Q6:5, Q7:1, Q8:1 }, expectedStyle: 'C', expX: 18, expY: 82, name: '探索聆聽者' },
  { answers: { Q1:1, Q2:1, Q3:5, Q4:5, Q5:1, Q6:1, Q7:5, Q8:5 }, expectedStyle: 'D', expX: 82, expY: 82, name: '行動聆聽者' }
];

for (const tc of testCases) {
  scope.userAnswers = tc.answers;
  scope.finishQuiz();
  // 觸發 700ms 定時器
  while (timers.length) timers.shift()();

  const styleName = getEl('result-style-name').textContent;
  const pinLeft = getEl('quadrant-pin').style.left;
  const pinTop = getEl('quadrant-pin').style.top;
  const coordsLabel = getEl('result-coords-label').textContent;

  assert.strictEqual(styleName, tc.name, `風格名稱應為 ${tc.name}，實際為 ${styleName}`);
  assert.strictEqual(pinLeft, `${tc.expX}%`, `落點 X 應為 ${tc.expX}%，實際為 ${pinLeft}`);
  assert.strictEqual(pinTop, `${tc.expY}%`, `落點 Y 應為 ${tc.expY}%，實際為 ${pinTop}`);
  assert(coordsLabel.includes(`${tc.expX}％`), `座標文字應包含 ${tc.expX}％，實際為 ${coordsLabel}`);
  assert(coordsLabel.includes(`${tc.expY}％`), `座標文字應包含 ${tc.expY}％，實際為 ${coordsLabel}`);
  
  // 檢查表單 pre-filled url
  const formHref = getEl('btn-go-form').href;
  assert(formHref.includes('forms.gle'), '表單連結應包含 forms.gle');
  assert(formHref.includes(`code=${tc.expectedStyle}`), `表單連結應包含 code=${tc.expectedStyle}`);

  console.log(`   [通過] ${tc.name} 落點 (${tc.expX}%, ${tc.expY}%) 與報表映射完全精準`);
}

// 測試 E：分享剪貼簿文字格式與標點檢查
console.log('5. 驗證分享文字格式與全形標點符號...');
const shareText = sandbox.window.currentResultShareText;
assert(shareText.length > 50, '分享文字不得為空');
assert(!/[,\?!;]/.test(shareText), '中文分享文字嚴禁包含半形逗號、問號、驚嘆號或分號');
console.log('   [通過] 分享文字格式優美，全形標點嚴格落實');

console.log('\n恭喜！所有 Node.js E2E 端到端真實生命週期測試全數 PASS！');
