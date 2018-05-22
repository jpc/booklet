window.model = {}

var o = ko.observable

model.even = {
  pages: _.filter(all_pages, x => x.even),
  crop: o(),
  edited: o(false),
}
model.odd = {
  pages: _.filter(all_pages, x => !x.even),
  crop: o(),
  edited: o(false),
}
model.even.linked = o(model.odd)
model.odd.linked = o(model.even)


function fmt(v) {
  return v.toFixed(3)
}
function fmtCrop(crop) {
  return !crop ? "" : `${fmt(crop.x)} ${fmt(crop.y)} ${fmt(crop.w)} ${fmt(crop.h)}`
}
model.crop = ko.computed(function() {
  var even_crop = model.even.crop(), odd_crop = model.odd.crop()
  if (even_crop == odd_crop)
    return even_crop
  else
    return `${even_crop} ${odd_crop}`
})

ko.applyBindings(model, document.body)

function ensureLoaded(img, callback) {
  if(img.complete)
    callback()
  else
    img.onload = callback
}

_.forEach(document.getElementsByClassName('page-container'), function (el) {
  var ctx = ko.dataFor(el)
  var canvas = document.createElement('canvas')
  canvas.width = 210 * 2; canvas.height = 297 * 2
  var cctx = canvas.getContext('2d', { preserveDrawingBuffer: true });
  cctx.globalCompositeOperation = 'darken'
  var i = ctx.pages.length
  _.forEach(ctx.pages, function (page) {
    var img = document.createElement('img')
    img.src = page.url
    ensureLoaded(img, () => {
      // console.log('img loaded', img, img.width, img.height);
      cctx.drawImage(img, 0, 0, canvas.width, canvas.height);
      i--
      if(!i) {
        el.appendChild(canvas)
        ctx.cropper = new Cropper(canvas, {
          aspectRatio: 210/297,
          zoomable: false,
          crop: function(event) {
            var ctx = ko.dataFor(el)
            ctx.crop(fmtCrop({
              x: event.detail.x / canvas.width,
              y: event.detail.y / canvas.height,
              w: event.detail.width / canvas.width,
              h: event.detail.height / canvas.height,
            }))
          },
          cropmove: function(event) {
            var ctx = ko.dataFor(el)
            ctx.edited(true)
            if (!ctx.linked().edited()) {
              // console.log('propagating', ctx, ctx.linked())
              ctx.linked().cropper.setCropBoxData(ctx.cropper.getCropBoxData())
            }
          },
        })
      }
    })
  })
})
