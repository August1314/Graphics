/**
 * 导出工具函数
 */

export function downloadFile(filename, content, mimeType = 'text/plain') {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.download = filename;
    link.href = url;
    link.click();
    URL.revokeObjectURL(url);
}

export function canvasToPNG(canvas, quality = 1.0) {
    return canvas.toDataURL('image/png', quality);
}

export function dataToJSON(data, prettyPrint = true) {
    return prettyPrint ? JSON.stringify(data, null, 2) : JSON.stringify(data);
}

export function downloadPNG(canvas, filename = 'image.png') {
    const dataURL = canvasToPNG(canvas);
    const link = document.createElement('a');
    link.download = filename;
    link.href = dataURL;
    link.click();
}

export function downloadJSON(data, filename = 'data.json') {
    const jsonString = dataToJSON(data, true);
    downloadFile(filename, jsonString, 'application/json');
}

export default { downloadFile, canvasToPNG, dataToJSON, downloadPNG, downloadJSON };
