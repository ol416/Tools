const xpath = "//*[@id=\"tab0\"]/div/span";
const iconAttribute = "icon";

function findElementsByXPath(xpath) {
  return document.evaluate(xpath, document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
}

function clickElementsWithAttribute(elements, attribute, values) {
  values.forEach(value => {
    elements.forEach(element => {
      if (element.getAttribute(attribute) === value) {
        element.click();
      }
    });
  });
}

function main() {
  const elements = findElementsByXPath(xpath);
  const input = prompt("请输入逗号分割的字符串：");
  const values = input.replace(/@&#xe/g, "#xe").replace(/&#xe/g, "#xe").split(",").map(value => value.trim());
    console.log(`values:${values},typeof:${typeof values}`);
  clickElementsWithAttribute(elements, iconAttribute, values);
}

main();