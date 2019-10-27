//
//  ViewController.swift
//  TescoScanner
//
//  Created by Kotov, Mykhailo on 26/10/2019.
//  Copyright © 2019 Kotov, Mykhailo. All rights reserved.
//

import UIKit
import Alamofire

struct Store: Codable {
    let name: String
    let id: String
}

class ViewController: UIViewController {

    private var stores = [
        Store(name: "Tesco 1", id: "fdacbf60-7b73-4678-86f4-266b86750e3b"),
        Store(name: "Tesco 2", id: "885629af-8579-4002-b00d-7988bcfbb2b3"),
        Store(name: "Tesco 3", id: "4a621863-e0e4-4ec5-91fc-03a189478c74"),
        Store(name: "Tesco 4", id: "e02b2b94-ee6d-45c5-b573-e14e1547432d"),
        Store(name: "Tesco 5", id: "820cab88-7e5a-49f4-bc03-6876d5d787cd")
    ]
    private let storeKey = "StoreId"

    var selectedStore: Store? = nil
    @IBOutlet var storePicker: UIPickerView!

    private let scanDelegate = CodeDelegate()
    private let errorDelegate = ErrorDelegate()
    private let dismissDelegate = DismissDelegate()

    override func viewDidLoad() {
        super.viewDidLoad()
//        if let data = UserDefaults.standard.value(forKey: storeKey) as? Data {
//            selectedStore = try? PropertyListDecoder().decode(Store.self, from: data)
//        }
        //guard selectedStore != nil else {
            getStores()
        //    return
        //}
//        DispatchQueue.main.asyncAfter(deadline: DispatchTime.now() + 0.004) {
//            self.showScanner(animated: false)
//        }
    }

    func getStores() {
//        AF.request(
//            "https://tesco-x.herokuapp.com/shops",
//            method: .get,
//            parameters: nil,
//            encoder: JSONParameterEncoder.default).response { response in
//            debugPrint(response)
//        }
        AF.request("https://tesco-x.herokuapp.com/shops", method: .get, encoding: JSONEncoding.default)
            .responseJSON { response in
                switch response.result {
                case .success(let json):
                    print(json)
                    DispatchQueue.main.async {
                        if let json2 = json as? [[String: Any]] {
                            self.stores = json2.compactMap{
                                guard
                                    let name =  $0["address"] as? String,
                                    let id = $0["id"] as? String
                                    else { return nil }
                                return Store(name: name, id: id)

 }                        }
                        self.storePicker.reloadAllComponents()

                    }
                case .failure(let error):
                    print(error)
                }
        }
    }

    @IBAction func selectAction(_ sender: Any) {
        showScanner(animated: true)
    }

    private func showScanner(animated: Bool) {
        let viewController = BarcodeScannerViewController()
        viewController.isOneTimeSearch = false
        viewController.codeDelegate = self.scanDelegate
        viewController.errorDelegate = self.errorDelegate
        viewController.dismissalDelegate = self.dismissDelegate
        viewController.storeId = selectedStore?.id

        // Change focus view style
        viewController.cameraViewController.barCodeFocusViewType = .twoDimensions
        // Set settings button text
        let title = NSAttributedString(
            string: "Settings",
            attributes: [.font: UIFont.boldSystemFont(ofSize: 17), .foregroundColor : UIColor.mainHigh]
        )
        viewController.cameraViewController.settingsButton.setAttributedTitle(title, for: UIControl.State())

        self.present(viewController, animated: animated, completion: nil)

    }

}

extension ViewController: UIPickerViewDataSource {
    func numberOfComponents(in pickerView: UIPickerView) -> Int {
        return 1
    }

    func pickerView(_ pickerView: UIPickerView, numberOfRowsInComponent component: Int) -> Int {
        return stores.count
    }
}

extension ViewController: UIPickerViewDelegate {
    func pickerView(_ pickerView: UIPickerView, didSelectRow row: Int, inComponent component: Int) {
        guard stores.count > row else { return }

        UserDefaults.standard.set(try? PropertyListEncoder().encode(stores[row]), forKey: storeKey)
        selectedStore = stores[row]
    }

    func pickerView(_ pickerView: UIPickerView, attributedTitleForRow row: Int, forComponent component: Int) -> NSAttributedString? {
        guard stores.count > row else { return nil }

        let attributes: [NSAttributedString.Key: Any] = [
            .font: FontStyle.roboBlack(24).new,
            .foregroundColor: UIColor.mainText
        ]
        let text = stores[row].name
        return NSAttributedString(string: text, attributes: attributes)
    }
}

class CodeDelegate: BarcodeScannerCodeDelegate {
    func scanner(_ controller: BarcodeScannerViewController, didCaptureCode code: String, type: String) {
        print("CODE: \(code), type: \(type)")
        controller.getData(code: QRCode(gtin: code, shop_id: controller.storeId ?? ""))
        DispatchQueue.main.asyncAfter(deadline: .now() + 1.5) {
            controller.reset(animated: true)
        }
    }
}

class ErrorDelegate: BarcodeScannerErrorDelegate {
    func scanner(_ controller: BarcodeScannerViewController, didReceiveError error: Error) {
        print("ERROR: \(error)")
    }
}

class DismissDelegate: BarcodeScannerDismissalDelegate {
    func scannerDidDismiss(_ controller: BarcodeScannerViewController) {
        controller.dismiss(animated: true, completion: nil)
        print("DISMISS:::")
    }
}
