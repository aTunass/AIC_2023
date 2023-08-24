const viRadio = document.getElementById('vi');
const enRadio = document.getElementById('en');
const searchButton = document.getElementById('search-button');
const searchAltButton = document.getElementById('show_images');
const re_rankButton = document.getElementById('re_ranking');

let searchText = document.getElementById("search-box").value;
let trans = 1;
let btn_text_serach = 0;
let btn_re_ranking = 0;
let currentURL = window.location.href; 
let image_path_search = ""
let image_video_search=""
const searchString = 'show_image_search';
const regex = new RegExp(searchString, 'i'); // 'i' ở đây có nghĩa không phân biệt chữ hoa chữ thường
const searchVideo = 'show_image_video';
const regex_video = new RegExp(searchVideo, 'i'); // 'i' ở đây có nghĩa không phân biệt chữ hoa chữ thường
let check_click=0;
let newWindow;
let image_path_new = ""
let totalImages = 0
let img_path_backup=""
let img_path_backup_video=""
const imagesPerPage = 42;
// Biến để theo dõi trang hiện tại
let currentPage = 1;
let run_image_search = 0;
let run_image_video = 0;

// const btn_reset=document.getElementById('reset')
// btn_reset.addEventListener('click', function() {
//     trans = 1;
//     btn_text_serach = 0;
//     check_click=0;
//     image_path_new = "";
//     image_path_search = "";
//     image_video_search = "";
//     currentPage = 1;
//     run_image_search = 0;
//     run_image_video = 0;
// });
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
re_rankButton.addEventListener('click', function() {
    searchText = document.getElementById("search-box").value;
    console.log('re-rank: ',searchText, trans);
    currentPage=1;
    reRanking(searchText, currentPage, trans);
    btn_re_ranking=1;
});
searchAltButton.addEventListener('click', function() {
    console.log('Show images clicked');
    check_click=0;
    if (regex.test(currentURL)) {
        run_image_search=1;
        Image_search(image_path_search, currentPage, run_image_search);
    }else if (regex_video.test(currentURL)){
        run_image_video=1;
        Image_video(image_video_search, currentPage, run_image_video);
    }else if(btn_re_ranking==1){
        reRanking(searchText, currentPage, trans);
    }
    else if (btn_text_serach==0){
        loadImagesForPage(currentPage);
    }else{
        searchByText(searchText, currentPage, trans);
    }
    // check_image();
    // Add alternative search logic here
});
// Số lượng ảnh hiển thị trong mỗi trang
// Function để thêm ảnh vào lưới
function addImagesToGrid(images, shouldAddBorder, imagesToBorder) {
    const imageContainer = document.getElementById("image-container");
    imageContainer.innerHTML = "";
    images.forEach(imagePath => {
        const imageItem = document.createElement("div");
        imageItem.className = "image-item";
        imageItem.style.backgroundImage = "url('" + imagePath + "')";
        if (shouldAddBorder) {
            if (imagesToBorder.includes(imagePath)) {

                imageItem.classList.add("green-border"); // Thêm lớp để có border xanh lá
            }
        }
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
        const imageVideoButton = document.createElement("button");
        imageVideoButton.className = "Image_video"
        imageVideoButton.textContent = "V-S";
        imageVideoButton.addEventListener("click", function() {
            image_video_search = imagePath
            Show_Image_video(imagePath);
        });
        const show_image_segment = document.createElement("button");
        show_image_segment.className = "show_image_segment"
        show_image_segment.textContent = "S-S";
        show_image_segment.addEventListener("click", function() {
            Show_image_segment(imagePath);
        });
        
        const imagePathSpan = document.createElement("span");
        imagePathSpan.className = "image-path";
        const imagePathParts = imagePath.split('/'); // Tách đường dẫn thành các phần
        const displayedPath = imagePathParts.slice(-3).join('/'); // Lấy ba phần cuối cùng và ghép lại
        imagePathSpan.textContent = displayedPath;
        // imageItem.appendChild(imagePathSpan);
        if (check_click==1){
            imageItem.appendChild(submitButton);
            imageItem.appendChild(newPageButton);
            imageItem.appendChild(imageVideoButton);
            imageItem.appendChild(show_image_segment);
            imageItem.appendChild(imagePathSpan);
        }
        
        imageContainer.appendChild(imageItem);
    });
}
const show_options = document.getElementById('images_search_button')
        show_options.addEventListener("click", function() {
            check_click=1;
            if (regex.test(currentURL)) {
                run_image_search=1;
                Image_search(image_path_search, currentPage, run_image_search);
            }else if (regex_video.test(currentURL)){
                run_image_video=1;
                Image_video(image_video_search, currentPage, run_image_video);
            }else if(btn_re_ranking==1){
                reRanking(searchText, currentPage, trans);
            }
            else if (btn_text_serach==0){
                loadImagesForPage(currentPage);
            }else{
                searchByText(searchText, currentPage, trans);
            }
        });
const Download_csv = document.getElementById('Download_csv')
        Download_csv.addEventListener("click", function() {
            Download_csv_file();
        });
const show_data = document.getElementById('show_csv')
        show_data.addEventListener("click", function() {
            Show_CSV();
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
            addImagesToGrid(data.results, false, []);
        })
        .catch(error => console.error('Error searching:', error));
}
function reRanking(text, page, trans) {
    fetch(`/re_ranking?query=${text}&trans=${trans}&page=${page}&per_page=${imagesPerPage}`)
        .then(response => response.json())
        .then(data => {
            addImagesToGrid(data.results, false, []);
        })
} 
function Image_search(imagePath, page, run_image_search){
    if (imagePath !== ""){
        img_path_backup = imagePath
        console.log("imagePath", imagePath)
    }
    fetch(`/image_search?page=${page}&per_page=${imagesPerPage}&imagePath=${encodeURIComponent(img_path_backup)}`)
        .then(response => response.json())
        .then(data => {
            const data_images_search = data.results
            console.log('page: ', page)
            if (run_image_search==1){
                addImagesToGrid(data_images_search, false, [])
            }
        })
        .catch(error => console.error('Error searching:', error));
}
function Image_video(imagePath, page, run_image_video){
    if (imagePath !== ""){
        img_path_backup_video = imagePath
        console.log("imagePath", imagePath)
    }
    fetch(`/image_video?page=${page}&per_page=${imagesPerPage}&imagePath=${encodeURIComponent(img_path_backup_video)}`)
        .then(response => response.json())
        .then(data => {
            const data_combine = data.result_combine
            const data_filter = data.result_filter
            console.log('page: ', page)
            if (run_image_video==1){
                addImagesToGrid(data_combine, true, data_filter)      
            }
        })
        .catch(error => console.error('Error searching:', error));
}
function Show_CSV(){
    const newWindow = window.open('/show_data');
    // newWindow.addEventListener('load', function() {
    //     newWindow.Image_search(imagePath, 1, 1);
    // });
}
function Show_Image_search(imagePath) {
    const newWindow = window.open(`/show_image_search?imagePath=${encodeURIComponent(imagePath)}`, '_blank');
    newWindow.addEventListener('load', function() {
        newWindow.Image_search(imagePath, 1, 1);
    });
}
function Show_Image_video(imagePath) {
    const newWindow = window.open(`/show_image_video?imagePath=${encodeURIComponent(imagePath)}`, '_blank');
    newWindow.addEventListener('load', function() {
        newWindow.Image_video(imagePath, 1, 1);
    });
}
function Show_image_segment(imagePath) {
    var newWindow = window.open(`/show_segment_image?imagePath=${encodeURIComponent(imagePath)}`, '_blank');
    var imageContent = '<img src="' + imagePath + '" alt="Hình ảnh">';
    newWindow.document.write(imageContent);
}
function Download_csv_file(){
    // Tạo yêu cầu tải xuống tệp CSV
    var xhr = new XMLHttpRequest();
    xhr.open("GET", "/download_csv", true);
    xhr.responseType = "blob"; // Định dạng dữ liệu nhận về là blob
    xhr.onload = function() {
        if (xhr.status === 200) {
            // Tạo một đối tượng URL để tạo liên kết tải xuống
            var url = URL.createObjectURL(xhr.response);
            
            // Tạo một thẻ a (liên kết ẩn) để thực hiện tải xuống
            var a = document.createElement("a");
            a.style.display = "none";
            a.href = url;
            a.download = "csv_data.csv"; // Tên tệp tải xuống
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
        }
    };
    xhr.send();
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
            addImagesToGrid(data.images, true, []);
        })
        .catch(error => console.error('Error fetching images:', error));
}
document.getElementById("nextPageButton").addEventListener("click", function() {
    currentPage++;
    console.log('page: ',currentPage)
    console.log('path_img_search', image_path_search)
    console.log('image_video_search: ', image_video_search)
    if (regex.test(currentURL)) {
        run_image_search=1;
        Image_search(image_path_search, currentPage, run_image_search);       
    }else if (regex_video.test(currentURL)){
        run_image_video=1;
        Image_video(image_video_search, currentPage, run_image_video);
    }else if(btn_re_ranking==1){
        reRanking(searchText, currentPage, trans);
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
        console.log('path_img_search', image_path_search)
        console.log('image_video_search: ', image_video_search)
        if (regex.test(currentURL)) {
            run_image_search=1;
            Image_search(image_path_search, currentPage, run_image_search);
        }else if (regex_video.test(currentURL)){
            run_image_video=1;
            Image_video(image_video_search, currentPage, run_image_video);
        }else if(btn_re_ranking==1){
            reRanking(searchText, currentPage, trans);
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



