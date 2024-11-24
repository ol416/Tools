const script = document.createElement('script');
script.src = 'https://cdn.sheetjs.com/xlsx-latest/package/dist/xlsx.full.min.js';
document.head.appendChild(script);
script.onload = () => console.log('xlsx.min.js 加载完成');

// 初始化 logid，基于时间戳生成初始值
let logid = BigInt(Date.now()) * BigInt(1e6);

// logid 自动生成
const getLogId = () => logid++;

// 获取指定路径的文件列表
const ls = async (path, page = 1) => {
    try {
        const response = await fetch(`https://pan.baidu.com/api/list?clienttype=0&app_id=250528&web=1&dp-logid=${getLogId()}&order=time&desc=1&dir=${path}&num=100&page=${page}`);
        const data = await response.json();
        return (data.list || []).map(item => ({
            path: item.path,
            isdir: item.isdir,
            server_filename: item.server_filename,
            real_category: item.real_category,
            thumbs: item.thumbs || null,
            md5: item.md5,
            size: item.size,
        }));
    } catch (error) {
        console.error(`Error fetching path: ${path}, page: ${page}`, error);
        return [];
    }
};

// 递归获取目录下所有文件
const ls_r = async (path, page = 1) => {
    const files = await ls(path, page);
    if (files.length === 100) {
        files.push(...await ls_r(path, page + 1));
    }
    for (const file of files) {
        if (file.isdir) {
            file.children = await ls_r(file.path);
        }
    }
    return files;
};

// 支持多路径遍历
const ls_multi = async (paths) => {
    let allFiles = [];
    for (const path of paths) {
        const files = await ls_r(path);
        allFiles = allFiles.concat(files);
    }
    return allFiles;
};

// 筛选文件（支持多种格式）
const filterFiles = (files, formats) => {
    return files.flatMap(file => {
        if (file.isdir) {
            return filterFiles(file.children || [], formats);
        }
        const extension = file.server_filename?.split('.').pop()?.toLowerCase();
        if (formats.includes(extension)) {
            return [file];
        }
        return [];
    });
};

// 导出为 CSV 格式（解决中文乱码问题）
const exportToCSV = (data, filename) => {
    const csvContent = [
        ['server_filename', 'real_category', 'thumbs_icon', 'thumbs_url1', 'thumbs_url2', 'thumbs_url3', 'md5', 'path', 'size'], // 表头
        ...data.map(row => [
            row.server_filename,
            row.real_category,
            row.thumbs?.icon || '',
            row.thumbs?.url1 || '',
            row.thumbs?.url2 || '',
            row.thumbs?.url3 || '',
            row.md5 || '',
            row.path || '',
            row.size || '',
        ]),
    ]
        .map(e => e.join(','))
        .join('\n');

    const bom = '\uFEFF'; // 添加 BOM 解决 Excel 乱码问题
    const blob = new Blob([bom + csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `${filename}.csv`;
    link.click();
};



// 导出为 Excel 格式（需引入 xlsx.min.js）
const exportToExcel = (data, filename) => {
    const sheet = XLSX.utils.json_to_sheet(data);
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, sheet, 'Sheet1');
    XLSX.writeFile(workbook, `${filename}.xlsx`);
};

// 主程序逻辑
try {
    // 要遍历的路径数组
    const paths = ['/path1']; // 可以添加更多路径 ['/path1', '/path2']

    // 获取所有路径下的文件
    const files = await ls_multi(paths);

    console.log('文件结构:', JSON.stringify(files, null, 2));

    // 筛选文件（支持的格式，例如 'jpg', 'png' 等）
    const supportedFormats = ['jpg', 'jpeg', 'png', 'gif'];
    const filteredFiles = filterFiles(files, supportedFormats);

    console.log('筛选结果:', filteredFiles);

    // 选择导出格式
    const exportChoice = prompt('请选择导出格式：输入 1 为 CSV，输入 2 为 Excel', '1');
    if (exportChoice === '1') {
        exportToCSV(filteredFiles, 'exported_data');
    } else if (exportChoice === '2') {
        if (typeof XLSX === 'undefined') {
            console.error('请确保加载了 xlsx.min.js 库！');
        } else {
            exportToExcel(filteredFiles, 'exported_data');
        }
    } else {
        console.log('取消导出。');
    }
} catch (error) {
    console.error('Error processing files:', error);
}
