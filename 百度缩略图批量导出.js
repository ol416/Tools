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
        return {
            files: (data.list || []).map(item => ({
                path: item.path,
                isdir: item.isdir,
                server_filename: item.server_filename,
                real_category: item.real_category,
                thumbs: item.thumbs || null,
                md5: item.md5,
                size: item.size,
            })),
            hasMore: data.list && data.list.length === 100 // 判断是否还有更多文件
        };
    } catch (error) {
        console.error(`Error fetching path: ${path}, page: ${page}`, error);
        return { files: [], hasMore: false };
    }
};

// 非递归获取目录下所有文件，支持分页
const ls_r_iterative = async (path) => {
    let stack = [path];
    let allFiles = [];

    while (stack.length > 0) {
        const currentPath = stack.pop();
        let page = 1;
        let hasMore = true;

        while (hasMore) {
            const { files, hasMore: more } = await ls(currentPath, page++);

            for (const file of files) {
                if (file.isdir) {
                    stack.push(file.path);
                } else {
                    allFiles.push(file);
                }
            }

            hasMore = more;
        }
    }

    return allFiles;
};

// 并发控制的批量获取
const fetchWithLimit = (paths, limit) => {
    const pool = Array(limit).fill(Promise.resolve());
    const results = [];

    for (const path of paths) {
        const current = pool.shift();
        const task = current.then(() => ls_r_iterative(path));
        pool.push(task);
        results.push(task);
    }

    return Promise.all(results).then(res => res.flat());
};

// 筛选文件（支持多种格式）
const filterFiles = (files, formats, cache = new Set()) => {
    return files.flatMap(file => {
        if (cache.has(file.path)) return []; // 跳过已处理
        cache.add(file.path);

        if (file.isdir) {
            return filterFiles(file.children || [], formats, cache);
        }

        const extension = file.server_filename?.split('.').pop()?.toLowerCase();
        return formats.includes(extension) ? [file] : [];
    });
};

// 通用文件下载链接
const downloadLink = document.createElement('a');
downloadLink.style.display = 'none';
document.body.appendChild(downloadLink);
const createDownload = (blob, filename) => {
    downloadLink.href = URL.createObjectURL(blob);
    downloadLink.download = filename;
    downloadLink.click();
    URL.revokeObjectURL(downloadLink.href); // 防止内存泄漏
};

// 进度显示
const showProgress = (current, total) => {
    console.log(`正在导出第 ${current}/${total} 个文件块...`);
};

// 导出为 CSV 格式（分块处理）
const exportToCSVInChunks = (data, filename, chunkSize = 10000) => {
    const bom = '\uFEFF'; // 添加 BOM 解决 Excel 乱码问题
    let chunkIndex = 1;

    for (let i = 0; i < data.length; i += chunkSize) {
        const chunk = data.slice(i, i + chunkSize);
        const csvContent = [
            ['server_filename', 'real_category', 'thumbs_icon', 'thumbs_url1', 'thumbs_url2', 'thumbs_url3', 'md5', 'path', 'size'], // 表头
            ...chunk.map(row => [
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

        const blob = new Blob([bom + csvContent], { type: 'text/csv;charset=utf-8;' });
        createDownload(blob, `${filename}_part${chunkIndex}.csv`);

        showProgress(chunkIndex, Math.ceil(data.length / chunkSize));
        chunkIndex++;
    }
};

// 导出为 Excel 格式（分块处理）
const exportToExcelInChunks = (data, filename, chunkSize = 10000) => {
    if (typeof XLSX === 'undefined') {
        console.error('请确保加载了 xlsx.min.js 库！');
        return;
    }

    let chunkIndex = 1;

    for (let i = 0; i < data.length; i += chunkSize) {
        const chunk = data.slice(i, i + chunkSize);
        const formattedChunk = chunk.map(row => ({
            server_filename: row.server_filename,
            real_category: row.real_category,
            thumbs_icon: row.thumbs?.icon || '',
            thumbs_url1: row.thumbs?.url1 || '',
            thumbs_url2: row.thumbs?.url2 || '',
            thumbs_url3: row.thumbs?.url3 || '',
            md5: row.md5 || '',
            path: row.path || '',
            size: row.size || ''
        }));
        const sheet = XLSX.utils.json_to_sheet(formattedChunk);
        const workbook = XLSX.utils.book_new();
        XLSX.utils.book_append_sheet(workbook, sheet, 'Sheet1');

        XLSX.writeFile(workbook, `${filename}_part${chunkIndex}.xlsx`);

        showProgress(chunkIndex, Math.ceil(data.length / chunkSize));
        chunkIndex++;
    }
};

// 主程序逻辑
try {
    // 动态获取 chunkSize
    const chunkSize = Number(prompt('请输入每块导出数据的行数（默认 100000）:', '100000')) || 100000;

    // 要遍历的路径数组
    const paths = ['/path1']; // 可以添加更多路径 ['/path1', '/path2']

    // 并发控制获取所有路径下的文件
    const files = await fetchWithLimit(paths, 5);

    console.log('文件结构:', JSON.stringify(files, null, 2));

    // 筛选文件（支持的格式，例如 'jpg', 'png' 等）
    const supportedFormats = ['jpg', 'jpeg', 'png', 'gif'];
    const filteredFiles = filterFiles(files, supportedFormats);

    console.log('筛选结果:', filteredFiles);

    // 选择导出格式并处理大文件导出
    const exportChoice = prompt('请选择导出格式：输入 1 为 CSV，输入 2 为 Excel', '1');

    if (exportChoice === '1') {
        exportToCSVInChunks(filteredFiles, 'exported_data', chunkSize);
    } else if (exportChoice === '2') {
        exportToExcelInChunks(filteredFiles, 'exported_data', chunkSize);
    } else {
        console.log('取消导出。');
    }

} catch (error) {
    console.error('Error processing files:', error);
}
