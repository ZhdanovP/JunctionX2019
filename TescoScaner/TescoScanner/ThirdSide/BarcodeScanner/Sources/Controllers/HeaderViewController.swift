import UIKit

/// Delegate to handle touch event of the close button.
protocol HeaderViewControllerDelegate: class {
  func headerViewControllerDidTapCloseButton(_ controller: HeaderViewController)
}

/// View controller with title label and close button.
/// It will be added as a child view controller if `BarcodeScannerController` is being presented.
public final class HeaderViewController: UIViewController {
  weak var delegate: HeaderViewControllerDelegate?

  // MARK: - UI properties

  /// Header view with title label and close button.
  public private(set) lazy var navigationBar: UINavigationBar = self.makeNavigationBar()
  /// Title view of the navigation bar.
  public private(set) lazy var titleLabel: UIImageView = self.makeTitleLabel()
  /// Left bar button item of the navigation bar.
  public private(set) lazy var closeButton: UIButton = self.makeCloseButton()

  // MARK: - View lifecycle

  public override func viewDidLoad() {
    super.viewDidLoad()

    navigationBar.delegate = self
    closeButton.addTarget(self, action: #selector(handleCloseButtonTap), for: .touchUpInside)

    view.addSubview(navigationBar)
    setupConstraints()
  }

  // MARK: - Actions

  @objc private func handleCloseButtonTap() {
    delegate?.headerViewControllerDidTapCloseButton(self)
  }

  // MARK: - Layout

  private func setupConstraints() {
    NSLayoutConstraint.activate(
      navigationBar.leadingAnchor.constraint(equalTo: view.leadingAnchor),
      navigationBar.trailingAnchor.constraint(equalTo: view.trailingAnchor)
    )

    if #available(iOS 11, *) {
      navigationBar.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor).isActive = true
    } else {
      navigationBar.topAnchor.constraint(equalTo: topLayoutGuide.bottomAnchor).isActive = true
    }
  }
}

// MARK: - Subviews factory

private extension HeaderViewController {
  func makeNavigationBar() -> UINavigationBar {
    let navigationBar = UINavigationBar()
    navigationBar.isTranslucent = false
    navigationBar.backgroundColor = .white
    navigationBar.items = [makeNavigationItem()]
    return navigationBar
  }

  func makeNavigationItem() -> UINavigationItem {
    let navigationItem = UINavigationItem()
    closeButton.sizeToFit()
    navigationItem.leftBarButtonItem = UIBarButtonItem(customView: closeButton)
    titleLabel.sizeToFit()
    navigationItem.titleView = titleLabel
    return navigationItem
  }

  func makeTitleLabel() -> UIImageView {
    let image = #imageLiteral(resourceName: "titleB")
    let label = UIImageView(image: image)
    return label
  }

  func makeCloseButton() -> UIButton {
    let button = UIButton(type: .system)
    button.setTitle(localizedString("Stores"), for: UIControl.State())
    button.titleLabel?.font = FontStyle.roboBold(17).new
    button.tintColor = .mainText
    return button
  }
}

// MARK: - UINavigationBarDelegate

extension HeaderViewController: UINavigationBarDelegate {
  public func position(for bar: UIBarPositioning) -> UIBarPosition {
    return .topAttached
  }
}
