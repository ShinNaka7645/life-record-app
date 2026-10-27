// ページの読み込みが完了したら以下の処理を実行
document.addEventListener('DOMContentLoaded', function() {
  // すべてのフラッシュ要素(クラス名が"flash")を取得
  var flashes = document.querySelectorAll('.flash');

  flashes.forEach(function(flash) {
    // 3秒後にフラッシュをフェードアウトして消す
    setTimeout(function() {
      flash.classList.add('fade-out');
      // フェードアウトが完了した後(0.5秒後)にフラッシュを削除
      setTimeout(function() {
        flash.remove();
      }, 500); // 0.5秒後
    }, 3000); // 3秒後
  });
});

document.addEventListener('DOMContentLoaded', function() {
  const menuToggle = document.getElementById('menuToggle');
  const headerMenu = document.getElementById('headerMenu');

  if (menuToggle && headerMenu) {
    menuToggle.addEventListener('click', function() {
      headerMenu.classList.toggle('active');
      menuToggle.classList.toggle('active');
    });
  }
});