import UIKit
import WebKit

final class ViewController: UIViewController, WKNavigationDelegate, WKUIDelegate, WKScriptMessageHandler {
    private var webView: WKWebView!

    override var preferredStatusBarStyle: UIStatusBarStyle {
        return .lightContent
    }

    override func viewDidLoad() {
        super.viewDidLoad()
        // Minh Phú Corporate Red status bar header background
        view.backgroundColor = UIColor(red: 0.60, green: 0.106, blue: 0.106, alpha: 1.0)

        let config = WKWebViewConfiguration()
        config.allowsInlineMediaPlayback = true
        config.preferences.javaScriptEnabled = true
        config.preferences.setValue(true, forKey: "allowFileAccessFromFileURLs")
        config.setValue(true, forKey: "allowUniversalAccessFromFileURLs")

        let controller = WKUserContentController()
        controller.add(self, name: "iosNative")
        config.userContentController = controller

        webView = WKWebView(frame: .zero, configuration: config)
        webView.translatesAutoresizingMaskIntoConstraints = false
        webView.navigationDelegate = self
        webView.uiDelegate = self
        webView.scrollView.bounces = false
        webView.backgroundColor = .white
        view.addSubview(webView)

        NSLayoutConstraint.activate([
            webView.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor),
            webView.leadingAnchor.constraint(equalTo: view.leadingAnchor),
            webView.trailingAnchor.constraint(equalTo: view.trailingAnchor),
            webView.bottomAnchor.constraint(equalTo: view.bottomAnchor)
        ])

        if let wwwUrl = Bundle.main.url(forResource: "index", withExtension: "html", subdirectory: "www") {
            let wwwDir = wwwUrl.deletingLastPathComponent()
            webView.loadFileURL(wwwUrl, allowingReadAccessTo: wwwDir)
        } else {
            let errHtml = """
            <html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
            <body style="font-family:-apple-system,sans-serif;padding:32px;text-align:center;">
              <h2 style="color:#991B1B;">Minh Phú HVAC</h2>
              <p>Không tìm thấy thư mục dữ liệu offline www/index.html trong gói ứng dụng.</p>
            </body></html>
            """
            webView.loadHTMLString(errHtml, baseURL: nil)
        }
    }

    func userContentController(_ userContentController: WKUserContentController, didReceive message: WKScriptMessage) {
        guard message.name == "iosNative",
              let body = message.body as? [String: Any],
              let action = body["action"] as? String else {
            return
        }

        if action == "openExternalUrl", let urlStr = body["url"] as? String, let url = URL(string: urlStr) {
            DispatchQueue.main.async {
                UIApplication.shared.open(url, options: [:], completionHandler: nil)
            }
        } else if action == "printPdf" {
            let jobName = (body["jobName"] as? String) ?? "Bao_Cao_Minh_Phu_HVAC"
            DispatchQueue.main.async {
                let printController = UIPrintInteractionController.shared
                let printInfo = UIPrintInfo(dictionary: nil)
                printInfo.jobName = jobName
                printInfo.outputType = .general
                printController.printInfo = printInfo
                printController.printFormatter = self.webView.viewPrintFormatter()
                printController.present(animated: true, completionHandler: nil)
            }
        }
    }

    func webView(
        _ webView: WKWebView,
        createWebViewWith configuration: WKWebViewConfiguration,
        for navigationAction: WKNavigationAction,
        windowFeatures: WKWindowFeatures
    ) -> WKWebView? {
        if let url = navigationAction.request.url {
            UIApplication.shared.open(url, options: [:], completionHandler: nil)
        }
        return nil
    }
}
