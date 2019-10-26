'use strict';

(function () {
  var $checkboxes = $('.shops__item input');

  $checkboxes.on('change', onShopChange);

  showFirstShop();

  function onShopChange(e) {
    var shopId = e.target.value;
    var latitude = e.target.getAttribute('data-latitude');
    var longitude = e.target.getAttribute('data-longitude');
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
    var $iframe = document.querySelector('.map iframe');
    var src = 'https://maps.google.com/maps?q=' + latitude + ',' + longitude + '&output=embed';
    $iframe.setAttribute('src', src);
  }

  function showFirstShop() {
    var $selectedShop = document.querySelector('.shops__item input:checked');
    if (!$selectedShop) {
      $selectedShop = document.querySelector('.shops__item input');
    }

    if ($selectedShop) {
      showShop($selectedShop.value);

      var latitude = $selectedShop.getAttribute('data-latitude');
      var longitude = $selectedShop.getAttribute('data-longitude');
      showMap(latitude, longitude);
    }
  }
})(jQuery);
//# sourceMappingURL=shops.js.map
