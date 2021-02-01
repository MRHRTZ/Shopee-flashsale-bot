const figlet = require('figlet')
const chalk = require('chalk')
const clear = require('clear')
const clui = require('clui')
const fs = require('fs')
const { Spinner } = clui
const cheerio = require('cheerio')
const puppeteer = require('puppeteer-extra')
const StealthPlugin = require('puppeteer-extra-plugin-stealth')
const inquirer = require('inquirer')
const status = new Spinner(chalk.yellow(`Sedang memproses data...`), ['⣾', '⣽', '⣻', '⢿', '⡿', '⣟', '⣯', '⣷'])
puppeteer.use(StealthPlugin())
const moment = require('moment')

// moment.tz.setDefault('Asia/Jakarta').locale('id')

const cek = moment()

function sleep(ms) {
    return new Promise((resolve) => {
        setTimeout(resolve, ms);
    });
}

function countDownDays(jammer) {
    var djam = jammer.split(':')[0],
        dmenit = jammer.split(':')[1],
        ddetik = jammer.split(':')[2];
    var datts = new Date();
    var process = datts.getTime()
    var countDownDate = moment(process).add(Number(djam), 'hours').add(Number(dmenit), 'minutes').add(Number(ddetik), 'seconds')
    // Update the count down every 1 second
    var x = setInterval(async function () {

        // Get today's date and time
        var now = new Date().getTime();
        // console.log(new Date().getDate())
        // Find the distance between now and the count down date
        var distance = countDownDate - now;

        // Time calculations for days, hours, minutes and seconds
        var days = Math.floor(distance / (1000 * 60 * 60 * 24));
        var hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
        var seconds = Math.floor((distance % (1000 * 60)) / 1000);

        // Display the result in the element with id="demo"
        const counter = days + "d " + hours + "h "
            + minutes + "m " + seconds + "s ";

        // If the count down is finished, write some text
        if (distance < 0) {
            clearInterval(x);
            return await sleep(console.log("WAKTU HABIS!"), 1000)
        }
        return await sleep(console.clear(), 1000) && await sleep(console.log(counter), 1000)
    }, 1000);
}





function title() {
    clear()
    console.log(
        chalk.bold.green(
            figlet.textSync('FS-Bot!', {
                font: 'Ghost',
                horizontalLayout: 'default',
                verticalLayout: 'default',
                width: 80,
                whitespaceBreak: true
            })
        )
    );
    console.log(chalk.green(`\n                        ${chalk.yellow('[ Created By MRHRTZ ]')}\n\n${chalk.red('Nama Bot')} : ${chalk.white('FS BOT v1')}\n${chalk.red('Follow Insta Dev')} : ${chalk.white('@hanif_az.sq.61')}\n`))

}

function autocheckout(url) {
    (async () => {
        try {
            status.start()
            let target_barang = [
                url
            ]

            const browser = await puppeteer.launch({
                headless: false,
                executablePath: 'C://Program Files//Google//Chrome//Application//chrome.exe',
                defaultViewport: null
            });
            const page = await browser.newPage();
            status.stop()
            const cookiesFilePath = './.datalog/cookies.json'
            const cookiesString = fs.readFileSync(cookiesFilePath);
            const parsedCookies = JSON.parse(cookiesString);
            if (parsedCookies.length !== 0) {
                for (let cookie of parsedCookies) {
                    await page.setCookie(cookie)
                }
                status.stop()
                clear()
                title()
                console.log(chalk.greenBright(`\n[✅] Data login berhasil dimuat`))
                status.start()
            }

            await page.goto(target_barang[0], { waitUntil: 'domcontentloaded' })
            const bodyHandle = await page.$('body');
            const html = await page.evaluate(body => body.innerHTML, bodyHandle);
            await bodyHandle.dispose();
            const $ = cheerio.load(html)
            status.stop()
            const tersisa = $('div > div > div.flex.items-center > div:nth-child(2)').text()
            const kirim = $('div.flex > div > div > div > span').text()
            const result = $('div > div.qaNIZv > span').text()
            const harga = $('div > div > div > div > div.flex.items-center > div._3n5NQx').text()
            const statusTersedia = $('button.btn.btn-solid-primary.btn--l.YtgjXY').attr('aria-disabled')
            const ada = statusTersedia == false ? true : false
            if (!ada) {
                console.log(chalk.green(`[✅] Berhasil dimasukan ke keranjang!`))
                // console.log(chalk.green(`[✅] Nama Barang : ${chalk.whiteBright(result)}`))
                // console.log(chalk.green(`[✅] Akan dikirim ke : ${chalk.whiteBright(kirim)}`))
                // console.log(chalk.green(`[✅] Barang tersisa : ${chalk.whiteBright(tersisa.replace('tersisa','').replace('buah',''))} buah`))
                // console.log(chalk.green(`[✅] Harga Flash Sale : ${chalk.whiteBright(harga)}\n`))
            } else {
                console.log(chalk.green("[X] Barangnya Abis Gan :("))
            }
            await page.waitForSelector('div > div > button.btn.btn-solid-primary.btn--l.YtgjXY')
            await page.click('div > div > button.btn.btn-solid-primary.btn--l.YtgjXY', { waitUntil: 'domcontentloaded' })
            // await page.waitForNavigation()
            await page.waitForSelector('div.cart-page-footer__checkout > button')
            await page.click('div.cart-page-footer__checkout > button', { waitUntil: 'domcontentloaded' })
            console.log(chalk.green(`[✅] Berhasil checkout`))

            //Metode Pembayaran
            const ShopeePay = 'div.checkout-payment-setting__payment-methods-tab > span:nth-child(1) > button'
            const TransferBank = 'div.checkout-payment-setting__payment-methods-tab > span:nth-child(2) > button'
            const KartuKredit = 'div.checkout-payment-setting__payment-methods-tab > span:nth-child(3) > button'
            const COD = 'div.checkout-payment-setting__payment-methods-tab > span:nth-child(4) > button'
            const CicilanKredit = 'div.checkout-payment-setting__payment-methods-tab > span:nth-child(5) > button'
            const Alfamart = 'div.checkout-payment-setting__payment-methods-tab > span:nth-child(6) > button'
            const Indomaret = 'div.checkout-payment-setting__payment-methods-tab > span:nth-child(7) > button'
            const OneKlik = 'div.checkout-payment-setting__payment-methods-tab > span:nth-child(8) > button'
            const Kredivo = 'div.checkout-payment-setting__payment-methods-tab > span:nth-child(9) > button'
            const Akulaku = 'div.checkout-payment-setting__payment-methods-tab > span:nth-child(10) > button'
            const methodpaym = JSON.parse(fs.readFileSync('./.datalog/data.json', 'utf8'))
            console.log(chalk.green(`[✅] Memilih metode pembayaran : ${methodpaym.payment}\n`))
            const pilihanpaym = methodpaym.payment
            const selbuy = '#main > div > div > div.page-checkout.container > div.page-checkout__payment-order-wrapper > div > div > button.stardust-button'
            switch (pilihanpaym) {
                case 'ShopeePay':
                    await page.waitForSelector(ShopeePay)
                    await page.waitForSelector(selbuy)
                    await page.click(ShopeePay)
                    await page.click(selbuy)
                    console.log(chalk.green('[✅] Berhasil dipesan, barang akan dikirim!'))
                    break;
                case 'TransferBank':
                    await page.waitForSelector(TransferBank)
                    await page.click(TransferBank)
                    await page.waitForSelector(selbuy)
                    await page.click(selbuy)
                    console.log(chalk.green('[✅] Berhasil dipesan, barang akan dikirim!'))
                    break;
                case 'KartuKredit':
                    await page.waitForSelector(KartuKredit)
                    await page.click(KartuKredit)
                    await page.waitForSelector(selbuy)
                    await page.click(selbuy)
                    console.log(chalk.green('[✅] Berhasil dipesan, barang akan dikirim!'))
                    break;
                case 'COD':
                    await page.waitForSelector(COD)
                    await page.click(COD)
                    await page.waitForSelector(selbuy)
                    await page.click(selbuy)
                    console.log(chalk.green('[✅] Berhasil dipesan, barang akan dikirim!'))
                    break;
                case 'CicilanKredit':
                    await page.waitForSelector(CicilanKredit)
                    await page.click(CicilanKredit)
                    await page.waitForSelector(selbuy)
                    await page.click(selbuy)
                    console.log(chalk.green('[✅] Berhasil dipesan, barang akan dikirim!'))
                    break;
                case 'Alfamart':
                    await page.waitForSelector(Alfamart)
                    await page.click(Alfamart)
                    await page.waitForSelector(selbuy)
                    await page.click(selbuy)
                    console.log(chalk.green('[✅] Berhasil dipesan, barang akan dikirim!'))
                    break;
                case 'Indomaret':
                    await page.waitForSelector(Indomaret)
                    await page.click(Indomaret)
                    await page.waitForSelector(selbuy)
                    await page.click(selbuy)
                    console.log(chalk.green('[✅] Berhasil dipesan, barang akan dikirim!'))
                    break;
                case 'OneKlik':
                    await page.waitForSelector(OneKlik)
                    await page.click(OneKlik)
                    await page.waitForSelector(selbuy)
                    await page.click(selbuy)
                    console.log(chalk.green('[✅] Berhasil dipesan, barang akan dikirim!'))
                    break;
                case 'Kredivo':
                    await page.waitForSelector(Kredivo)
                    await page.click(Kredivo)
                    await page.waitForSelector(selbuy)
                    await page.click(selbuy)
                    console.log(chalk.green('[✅] Berhasil dipesan, barang akan dikirim!'))
                    break;
                case 'Akulaku':
                    await page.waitForSelector(Akulaku)
                    await page.click(Akulaku)
                    await page.waitForSelector(selbuy)
                    await page.click(selbuy)
                    console.log(chalk.green('[✅] Berhasil dipesan, barang akan dikirim!'))
                    break;
                default:
                    break;
            }
            //#main > div > div._1Bj1VS > div.page-product > div.container > div.product-briefing.flex.card._2cRTS4 > div.flex.flex-auto.k-mj2F > div > div._3DepLY > div > div.flex._3dRJGI._3a2wD-._2OPYmZ > div > div:nth-child(1) > div > button:nth-child(1)
            // await browser.close();
            // await page.waitForSelector('div.page-checkout.container > div.page-checkout__payment-order-wrapper > div > div > button')
        } catch (e) {
            console.log(e)
        }

    })();
}


function ceklogin() {
    return new Promise(async (resolve, reject) => {
        try {
            status.start()
            const cookiesFilePath = './.datalog/cookies.json';
            const previousSession = fs.existsSync(cookiesFilePath)
            if (previousSession) {
                status.stop()
                clear()
                title()
                console.log(chalk.blueBright("[✅] Telah login"))
                return true
                // If file exist load the cookies
                const cookiesString = fs.readFileSync(cookiesFilePath);
                const parsedCookies = JSON.parse(cookiesString);
                if (parsedCookies.length !== 0) {
                    for (let cookie of parsedCookies) {
                        await page.setCookie(cookie)
                    }
                    console.log('Session has been loaded in the browser')
                }
            } else {
                console.log(chalk.cyan(`=> [ Login Shopee Dibutuhkan ] <=\n`))
                let login_page = [
                    "https://shopee.co.id/buyer/login?next=https%3A%2F%2Fshopee.co.id%2Flogin"
                ]

                const browser = await puppeteer.launch({
                    headless: false,
                    executablePath: 'C://Program Files//Google//Chrome//Application//chrome.exe',
                    defaultViewport: null
                });

                const page = await browser.newPage();
                page.setDefaultNavigationTimeout(10000000)

                await page.goto(login_page[0], { waitUntil: "networkidle2" });

                const GoogleLogin = await page.$('button._35rr5y._32qX4k._3Bn0WQ.WEKQ8O.a6g9DN') //Gbsa
                const FbLogin = await page.$('button._35rr5y._32qX4k._3Bn0WQ.WEKQ8O._1lANZ5')
                const AppleLogin = await page.$('button._35rr5y._32qX4k._3Bn0WQ.WEKQ8O._3t9SSB')
                // await FbLogin.click()
                // console.log('klik,,')
                // const bodyHandle = await page.$('body');
                // const html = await page.evaluate(body => body.innerHTML, bodyHandle);
                // await bodyHandle.dispose();
                //083843103362
                // await page.waitForNavigation()
                const selector = 'div.shopee-searchbar > div > form > input';
                await page.waitForSelector(selector)
                const cookiesObject = await page.cookies()
                // Write cookies to temp file to be used in other profile pages
                fs.writeFile(cookiesFilePath, JSON.stringify(cookiesObject, null, 2),
                    function (err) {
                        if (err) {
                            console.log('Tidak bisa save file.', err)
                        }
                        status.stop()
                        console.log(chalk.green('Berhasil login!'))
                        return true
                    })
                await browser.close();
            }
        } catch (e) {
            // console.log(e)
        }
    })
}


async function mulai(url) {
    try {
        if (!fs.existsSync('./.datalog/')) fs.mkdirSync('./.datalog/')
        title()
        inquirer
            .prompt([{
                name: "url",
                type: "input",
                message: "Masukan Url Barang Flash Sale Shopee : ",
                validate: function (value) {
                    if (value.length) {
                        return true
                    } else {
                        return "Masukan link barang shopeenya yachh!"
                    }
                }
            }, {
                name: "date",
                type: "input",
                message: "Hitungan mundur dari (00:00:00) : ",
                mask: true,
                validate: function (value) {
                    if (value.length) {
                        return true
                    } else {
                        return "Masukin Jam Mulainya! lebih bagus kurangin 2-5 detik."
                    }
                }
            }, {
                name: "payment",
                type: "list",
                message: "Pilih Metode Pembayaran ( Penting! Cek kembali metode pembayaran yang tersedia. )",
                choices: ["ShopeePay", "TransferBank", "KartuKredit", "COD", "CicilanKredit", "Alfamart", "Indomaret", "OneKlik", "Kredivo", "Akulaku"]
            }, {
                name: "status",
                type: "confirm",
                message: "Data ini benar?"
            }])
            .then((data) => {
                if (data.status == false) {
                    console.log(chalk.red(`\nData tidak benar mohon login ulang!\n`))
                    return mulai()
                } else {
                    clear()
                    title()
                    console.log(chalk.yellow('Good luck :)'))
                    let waktfs = countDownDays(`12-14-2020 14:01`)
                    fs.writeFileSync('./.datalog/data.json', JSON.stringify(data, null, 2))
                    ceklogin().then(() => {
                        const hitungmundur = countDownDays((JSON.parse(fs.readFileSync('./.datalog/data.json'))).date)
                        // console.log(`Menunggu Flash Sale Dimulai ${waktfs}`)
                        if (hitungmundur) {
                            const { url } = JSON.parse(fs.readFileSync('./.datalog/data.json', 'utf8'))
                            autocheckout(url)
                        }
                    })
                    // else {
                    //     function intervalFunc() {
                    //         console.log(`Menunggu Flash Sale Dimulai ${waktfs}`)
                    //     }

                    //     setInterval(intervalFunc, 1000)

                    // }

                    /*<--- Proses login --->*/
                }
            })
        // status.stop()
    } catch (e) {
        console.log(e.title)
    }
}




mulai()
// ceklogin()
// autocheckout()


