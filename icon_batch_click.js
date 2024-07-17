const xpath = '//*[@id="tab0"]/div/span';
const iconAttribute = "icon";

function findElementsByXPath(xpath) {
  return document.evaluate(xpath, document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
}

function clickElementsWithAttribute(elements, attribute, values) {
  values.forEach((value) => {
    for (let i = 0; i < elements.snapshotLength; i++) {
      const element = elements.snapshotItem(i);
      if (element.getAttribute(attribute).includes(value)) {
        element.click();
        break; // 如果找到一个匹配的元素，就点击它并跳出循环
      }
    }
  });
}

function main() {
  const elements = findElementsByXPath(xpath);
  const input = prompt("请输入逗号分割的字符串：");
  if (input) {
    const values = input.replace(/@&#xe/g, "#xe").replace(/&#xe/g, "#xe").split(",").map(value => value.trim());
    console.log(`values: ${values}|typeof:${typeof values}`);
    clickElementsWithAttribute(elements, iconAttribute, values);
  } else {
    console.log("用户取消了输入或没有输入任何内容。");
  }
}

main();
