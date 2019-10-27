//
//  Styles.swift
//  TescoScaner
//
//  Created by Kotov, Mykhailo on 26/10/2019.
//  Copyright © 2019 Kotov, Mykhailo. All rights reserved.
//

import UIKit

extension UIColor {
    static let mainPrimary = #colorLiteral(red: 0, green: 0.6712427735, blue: 0.9576479793, alpha: 1)
    static let mainHigh = #colorLiteral(red: 0.9538398385, green: 0.2118341327, blue: 0.1828263104, alpha: 1)
    static let mainText = #colorLiteral(red: 0.2605174184, green: 0.2605243921, blue: 0.260520637, alpha: 1)
    static let mainFill1 = #colorLiteral(red: 0.9999960065, green: 1, blue: 1, alpha: 1)
    static let mainFill2 = #colorLiteral(red: 0.9719446301, green: 0.9719673991, blue: 0.9719551206, alpha: 1)
}

enum FontStyle {
    case roboLight(CGFloat)
    case roboReg(CGFloat)
    case roboMid(CGFloat)
    case roboBold(CGFloat)
    case roboBlack(CGFloat)

    var new: UIFont {
        switch self {
        case .roboLight(let size):
            return UIFont(name: "Roboto-Light", size: size) ?? UIFont.systemFont(ofSize: size)
        case .roboReg(let size):
            return UIFont(name: "Roboto-Regular", size: size) ?? UIFont.systemFont(ofSize: size)
        case .roboMid(let size):
            return UIFont(name: "Roboto-Medium", size: size) ?? UIFont.systemFont(ofSize: size)
        case .roboBold(let size):
            return UIFont(name: "Roboto-Bold", size: size) ?? UIFont.boldSystemFont(ofSize: size)
        case .roboBlack(let size):
            return UIFont(name: "Roboto-Black", size: size) ?? UIFont.boldSystemFont(ofSize: size)
        }
    }
}
