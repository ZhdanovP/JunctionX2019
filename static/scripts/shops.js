'use strict';

(function () {
  var $checkboxes = $('.shops__item input');

  $checkboxes.on('change', onShopChange);

  showFirstShop();

  function onShopChange(e) {
    var shopId = e.target.value;
    shopId && showShop(shopId);
  }

  function showShop(shopId) {
    if (!shopId) {
      return;
    }
    $('.goods__section--visible').removeClass('goods__section--visible');
    $('[data-shop-id="' + shopId + '"]').addClass('goods__section--visible');
  }

  function showFirstShop() {
    var $selectedShop = document.querySelector('.shops__item input:checked');
    if (!$selectedShop) {
      $selectedShop = document.querySelector('.shops__item input');
    }

    if ($selectedShop) {
      showShop($selectedShop.value);
    }
  }
})(jQuery);
//# sourceMappingURL=shops.js.map
