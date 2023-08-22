let currentPage = 1
const pageSize = 5
const itemEls = []
let prevBtn = null
let nextBtn = null
const pageBtnList = []

function updateBtn() {
    if (currentPage === 1) {
        prevBtn.classList.add('disabled')
        prevBtn.classList.remove('waves-effect')
    } else {
        prevBtn.classList.remove('disabled')
        prevBtn.classList.add('waves-effect')
    }
    if (currentPage === Math.ceil(itemEls.length / pageSize)) {
        nextBtn.classList.add('disabled')
        nextBtn.classList.remove('waves-effect')
    } else {
        nextBtn.classList.remove('disabled')
        nextBtn.classList.add('waves-effect')
    }
    pageBtnList.forEach((el, idx) => {
        if (idx + 1 === currentPage) {
            el.classList.add('active')
            el.classList.remove('waves-effect')
        } else {
            el.classList.remove('active')
            el.classList.add('waves-effect')
        }
    })
}

function prevPage() {
    updateBtn()
    if (currentPage === 1) return
    currentPage--
    goToPage(currentPage)
}

function nextPage() {
    updateBtn()
    if (currentPage === Math.ceil(itemEls.length / pageSize)) return
    currentPage++
    goToPage(currentPage)
}

function goToPage(page) {
    currentPage = page
    itemEls.forEach((el, idx) => {
        if (idx >= (currentPage - 1) * pageSize && idx < currentPage * pageSize) {
            el.style.display = 'block'
        } else {
            el.style.display = 'none'
        }
    })
    updateBtn()
}

addEventListener('DOMContentLoaded', function () {
    const els = document.querySelectorAll('div.podcast-item')
    els.forEach((el, idx) => {
        if (idx < pageSize) {
            el.style.display = 'block'
        }
        itemEls.push(el)
    })
    prevBtn = document.querySelector('ul.pagination > .prev')
    nextBtn = document.querySelector('ul.pagination > .next')
    prevBtn.addEventListener('click', prevPage)
    nextBtn.addEventListener('click', nextPage)
    const totalPage = Math.ceil(itemEls.length / pageSize)
    const paginationEl = document.querySelector('ul.pagination')
    for (let i = 1; i <= totalPage; i++) {
        const liEl = document.createElement('li')
        pageBtnList.push(liEl)
        if (i === currentPage) {
            liEl.classList.add('active')
            liEl.classList.remove('waves-effect')
        }
        const aEl = document.createElement('a')
        aEl.innerText = i
        aEl.style.cursor = 'pointer'
        liEl.appendChild(aEl)
        paginationEl.insertBefore(liEl, nextBtn)
        liEl.addEventListener('click', function () {
            goToPage(i)
        })
    }
})