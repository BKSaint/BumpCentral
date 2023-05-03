var cropper = new Cropper(document.getElementById('profile-picture'), {
    aspectRatio: 1 / 1,
    crop: function(event) {
      document.getElementById('crop-area').innerHTML = '<input type="hidden" name="x" value="' + event.detail.x + '">' +
                                                       '<input type="hidden" name="y" value="' + event.detail.y + '">' +
                                                       '<input type="hidden" name="width" value="' + event.detail.width + '">' +
                                                       '<input type="hidden" name="height" value="' + event.detail.height + '">';
    }
  });