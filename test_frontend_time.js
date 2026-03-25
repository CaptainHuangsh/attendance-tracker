// 模拟前端时间处理
console.log("=== 前端时间处理测试 ===");

// 模拟用户选择 2026-03-19 08:06
const dateStr = "2026-03-19";
const timeStr = "08:06";
const datetimeStr = `${dateStr}T${timeStr}`;

console.log(`用户选择: ${datetimeStr}`);

// 方法1: 使用Date对象（可能有时区问题）
const dt = new Date(datetimeStr);
console.log(`\n方法1: new Date("${datetimeStr}")`);
console.log(`  Date对象: ${dt}`);
console.log(`  toISOString(): ${dt.toISOString()}`);
console.log(`  getFullYear(): ${dt.getFullYear()}`);
console.log(`  getMonth()+1: ${dt.getMonth() + 1}`);
console.log(`  getDate(): ${dt.getDate()}`);
console.log(`  getHours(): ${dt.getHours()}`);
console.log(`  getMinutes(): ${dt.getMinutes()}`);

// 方法2: 直接解析字符串（避免Date对象时区问题）
console.log(`\n方法2: 直接解析字符串`);
const [datePart, timePart] = datetimeStr.split('T');
const [year, month, day] = datePart.split('-');
const [hours, minutes] = timePart.split(':');
console.log(`  直接解析结果: ${year}-${month}-${day} ${hours}:${minutes}:00`);

// 测试不同时区的影响
console.log(`\n=== 时区影响测试 ===`);
console.log(`当前时区偏移: ${dt.getTimezoneOffset()} 分钟`);
console.log(`UTC时间: ${dt.getUTCHours()}:${dt.getUTCMinutes()}`);

// 如果用户在中国（UTC+8），而服务器在UTC时区
const utcHours = dt.getUTCHours();
const localHours = dt.getHours();
console.log(`\n时区转换:`);
console.log(`  本地时间 ${localHours}:${dt.getMinutes()} (中国时间)`);
console.log(`  UTC时间 ${utcHours}:${dt.getUTCMinutes()}`);
console.log(`  时区差: ${localHours - utcHours} 小时`);

// 问题重现
console.log(`\n=== 问题重现 ===`);
console.log(`假设:`);
console.log(`  1. 用户在中国时间 08:06 上班`);
console.log(`  2. 前端使用 toISOString() 发送时间`);
console.log(`  3. 后端直接存储时间字符串`);

const chineseTime = "2026-03-19T08:06:00";
const dtChinese = new Date(chineseTime);
const isoString = dtChinese.toISOString(); // 2026-03-19T00:06:00.000Z
console.log(`\n中国时间: ${chineseTime}`);
console.log(`toISOString(): ${isoString}`);
console.log(`存储到数据库: ${isoString.split('T')[0]} ${isoString.split('T')[1].substring(0, 8)}`);
console.log(`结果: 08:06 变成了 00:06 (少了8小时)`);