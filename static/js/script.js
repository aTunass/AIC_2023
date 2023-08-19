const viRadio = document.getElementById('vi');
const enRadio = document.getElementById('en');
const searchButton = document.getElementById('search-button');
const searchAltButton = document.getElementById('show_images');
let searchText = document.getElementById("search-box").value;
let trans = 1;
let btn_text_serach = 0;
let currentURL = window.location.href;
let image_path_search = ""
const searchString = 'show_image_search';
const regex = new RegExp(searchString, 'i'); // 'i' ở đây có nghĩa không phân biệt chữ hoa chữ thường
let check_click=0;
let newWindow;
let image_path_new = ""
let totalImages = 0
const imagesPerPage = 42;
// Biến để theo dõi trang hiện tại
let currentPage = 1;
let run_image_search = 0;

const btn_reset=document.getElementById('reset')
btn_reset.addEventListener('click', function() {
    trans = 1;
    btn_text_serach = 0;
    check_click=0;
    image_path_new = "";
    image_path_search = "";
    currentPage = 1;
    run_image_search = 0;
});
viRadio.addEventListener('change', function() {
    if (viRadio.checked) {
        console.log('Selected language: Vietnamese');
        trans = 0
    }
});

enRadio.addEventListener('change', function() {
    if (enRadio.checked) {
        console.log('Selected language: English');
        trans = 1;
    }
});

searchButton.addEventListener('click', function() {
    searchText = document.getElementById("search-box").value;
    console.log('search box: ',searchText, trans);
    currentPage=1;
    searchByText(searchText, currentPage, trans);
    btn_text_serach=1;
});
searchAltButton.addEventListener('click', function() {
    console.log('Show images clicked');
    check_click=0;
    if (btn_text_serach==0){
        currentPage=1;
        loadImagesForPage(currentPage);
    }else{
        searchByText(searchText, currentPage, trans);
    }
    // check_image();
    // Add alternative search logic here
});
// Số lượng ảnh hiển thị trong mỗi trang
// Function để thêm ảnh vào lưới
function addImagesToGrid(images) {
    const imageContainer = document.getElementById("image-container");
    imageContainer.innerHTML = "";
    images.forEach(imagePath => {
        const imageItem = document.createElement("div");
        imageItem.className = "image-item";
        imageItem.style.backgroundImage = "url('" + imagePath + "')";

        // Thêm sự kiện click cho mỗi bức ảnh
        imageItem.addEventListener("click", function() {
            // Lấy phần tử chứa thông tin ảnh
            const infoText = document.getElementById('info-text');
            // Hiển thị đường dẫn ảnh trong phần thông tin
            let path_short = shortenImagePath(imagePath);
            image_path_new = imagePath;
            infoText.textContent = `${path_short}`;
            check_click=1;
        });
        // const image_search_btn = document.getElementById('images_search_button')
        // image_search_btn.addEventListener("click", function() {
        //     image_path_search = image_path_new
        //     Show_Image_search(image_path_new);
        //     currentPage=1;
        //     Image_search(image_path_new, currentPage, 1);
        // });
        
        const submitButton = document.createElement("button");
        submitButton.className = "submit-button";
        submitButton.textContent = "S-M";
        submitButton.addEventListener("click", function() {
            handleImageSubmit(imagePath);
        });
        
        const newPageButton = document.createElement("button");
        newPageButton.className = "Image_search";
        newPageButton.textContent = "I-S";
        newPageButton.addEventListener("click", function() {
            image_path_search = imagePath
            Show_Image_search(imagePath);
        });
        
        const imagePathSpan = document.createElement("span");
        imagePathSpan.className = "image-path";
        imagePathSpan.textContent = imagePath;
        // imageItem.appendChild(imagePathSpan);
        if (check_click==1){
            imageItem.appendChild(submitButton);
            imageItem.appendChild(newPageButton);
        }
        
        imageContainer.appendChild(imageItem);
    });
}
const show_options = document.getElementById('images_search_button')
        show_options.addEventListener("click", function() {
            check_click=1;
            if (btn_text_serach==0){
                loadImagesForPage(currentPage);
            }else{
                searchByText(searchText, currentPage, trans);
            }
        });
function shortenImagePath(fullPath) {
    const parts = fullPath.split('/');
    if (parts.length >= 3) {
        return parts.slice(2).join('/');
    }
    return fullPath;
}
function searchByText(text, page, trans) {
    fetch(`/text_search?query=${text}&trans=${trans}&page=${page}&per_page=${imagesPerPage}`)
        .then(response => response.json())
        .then(data => {
            addImagesToGrid(data.results);
        })
        .catch(error => console.error('Error searching:', error));
}
function Image_search(imagePath, page, run_image_search){
    fetch(`/image_search?page=${page}&per_page=${imagesPerPage}&imagePath=${encodeURIComponent(imagePath)}`)
        .then(response => response.json())
        .then(data => {
            const data_images_search = data.results
            console.log('page: ', page)
            if (run_image_search==1){
                addImagesToGrid(data_images_search)
            }
        })
        .catch(error => console.error('Error searching:', error));
}
function Show_Image_search(imagePath) {
    newWindow = window.open(`/show_image_search?imagePath=${encodeURIComponent(imagePath)}`, '_blank');
    newWindow.addEventListener('load', function() {
        newWindow.Image_search(imagePath, 1, 1);
    });
}

function handleImageSubmit(imagePath) {
    // Gửi đường dẫn ảnh lên server (Flask) để xử lý
    fetch('/submit_image', {
        method: 'POST',
        body: JSON.stringify({ imagePath: imagePath }),
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        // Xử lý kết quả trả về từ server (data)
        console.log(data);
    })
    .catch(error => console.error('Error submitting image:', error));
}
// Function để tải ảnh cho trang hiện tại
function loadImagesForPage(page) {
    fetch(`/get_images?page=${page}&per_page=${imagesPerPage}`)
        .then(response => response.json())
        .then(data => {
            totalImages = data.totalImages; 
            addImagesToGrid(data.images);
        })
        .catch(error => console.error('Error fetching images:', error));
}
document.getElementById("nextPageButton").addEventListener("click", function() {
    currentPage++;
    console.log('page: ',currentPage)
    if (regex.test(currentURL)) {
        run_image_search=1;
        Image_search(image_path_search, currentPage, run_image_search);       
    }
    else if (btn_text_serach==0){
        loadImagesForPage(currentPage);
    }else{
        searchByText(searchText, currentPage, trans);
    }
});
// Xử lý sự kiện khi người dùng nhấp vào nút "Previous Page"
document.getElementById("prevPageButton").addEventListener("click", function() {
    if (currentPage > 1) {
        currentPage--;
        console.log('page: ',currentPage)
        if (regex.test(currentURL)) {
            run_image_search=1;
            Image_search(image_path_search, currentPage, run_image_search);
        }
        else if (btn_text_serach==0){
            loadImagesForPage(currentPage);
        }else{
            searchByText(searchText, currentPage, trans);
        }
    }
});
// Xử lý sự kiện khi người dùng nhấn nút xóa
document.getElementById("clearButton").addEventListener("click", function() {
    document.getElementById("search-box").value = "";
    searchText = ""; // Cập nhật biến toàn cục searchText
});



