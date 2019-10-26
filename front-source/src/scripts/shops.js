(function() {
  var $checkboxes = $('.shops__item input');

  $checkboxes.on('change', onShopChange);

  showFirstShop();

  function onShopChange(e) {
    const shopId = e.target.value;
    const latitude = e.target.getAttribute('data-latitude');
    const longitude = e.target.getAttribute('data-longitude');
    shopId && showShop(shopId);
    showMap(latitude, longitude);
  }

  function showShop(shopId) {
    if (!shopId) {
      return;
    }
    $('.goods__section--visible').removeClass('goods__section--visible');
    $('[data-shop-id="' + shopId + '"]').addClass('goods__section--visible');
  }
  
  function showMap(latitude, longitude) {
    const $iframe = document.querySelector('.map iframe');
    const src = `https://maps.google.com/maps?q=${latitude},${longitude}&output=embed`;
    $iframe.setAttribute('src', src);
  }

  function showFirstShop() {
    let $selectedShop = document.querySelector('.shops__item input:checked');
    if (!$selectedShop) {
      $selectedShop = document.querySelector('.shops__item input');
    }

    if ($selectedShop) {
      showShop($selectedShop.value);

      const latitude = $selectedShop.getAttribute('data-latitude');
      const longitude = $selectedShop.getAttribute('data-longitude');
      showMap(latitude, longitude);
    }
  }
})(jQuery);
