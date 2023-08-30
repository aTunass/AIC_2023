function addImagesToGrid(images) {
    const imageContainer = document.getElementById("image-container");
    imageContainer.innerHTML = "";
    images.forEach(imagePath => {
        const imageItem = document.createElement("div");
        imageItem.className = "image-item";
        imageItem.style.backgroundImage = "url('" + imagePath + "')";
        imageContainer.appendChild(imageItem);
    });
}