document.addEventListener("DOMContentLoaded", function () {
  const minusBtn = document.querySelector(".qty-minus");
  const plusBtn = document.querySelector(".qty-plus");
  const qtyInput = document.querySelector(".qty-input");

  if (minusBtn && plusBtn && qtyInput) {
    plusBtn.addEventListener("click", function () {
      let currentQty = parseInt(qtyInput.value);
      const max = parseInt(qtyInput.max) || 99;

      if (currentQty < max) {
        qtyInput.value = currentQty + 1;
      }
    });

    minusBtn.addEventListener("click", function () {
      let currentQty = parseInt(qtyInput.value);

      if (currentQty > 1) {
        qtyInput.value = currentQty - 1;
      }
    });
  }
});
