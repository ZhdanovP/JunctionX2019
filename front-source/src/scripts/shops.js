(function() {
  var $checkboxes = $('.shops__item input');

  $checkboxes.on('change', onShopChange);

  showFirstShop();

  function onShopChange(e) {
    const shopId = e.target.value;
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
    let $selectedShop = document.querySelector('.shops__item input:checked');
    if (!$selectedShop) {
      $selectedShop = document.querySelector('.shops__item input');
    }

    if ($selectedShop) {
      showShop($selectedShop.value);
    }
  }
})(jQuery);
