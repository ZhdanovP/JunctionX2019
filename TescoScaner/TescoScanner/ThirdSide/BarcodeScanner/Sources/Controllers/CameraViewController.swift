import UIKit
import AVFoundation

/// Delegate to handle camera setup and video capturing.
protocol CameraViewControllerDelegate: class {
    func cameraViewControllerDidSetupCaptureSession(_ controller: CameraViewController)
    func cameraViewControllerDidFailToSetupCaptureSession(_ controller: CameraViewController)
    func cameraViewController(_ controller: CameraViewController, didReceiveError error: Error)
    func cameraViewControllerDidTapSettingsButton(_ controller: CameraViewController)
    func cameraViewController(
        _ controller: CameraViewController,
        didOutput metadataObjects: [AVMetadataObject]
    )
}

/// View controller responsible for camera controls and video capturing.
public final class CameraViewController: UIViewController {
    weak var delegate: CameraViewControllerDelegate?

    /// Focus view type.
    public var barCodeFocusViewType: FocusViewType = .animated
    public var showsCameraButton: Bool = false {
        didSet {
            cameraButton.isHidden = showsCameraButton
        }
    }
    /// `AVCaptureMetadataOutput` metadata object types.
    var metadata = [AVMetadataObject.ObjectType]()

    // MARK: - UI proterties

    /// Animated focus view.
    public private(set) lazy var focusView: UIView = self.makeFocusView()
    /// Button to change torch mode.
    public private(set) lazy var flashButton: UIButton = .init(type: .custom)
    /// Button that opens settings to allow camera usage.
    public private(set) lazy var settingsButton: UIButton = self.makeSettingsButton()
    // Button to switch between front and back camera.
    public private(set) lazy var cameraButton: UIButton = self.makeCameraButton()
    // Button to switch between front and back camera.
    public private(set) lazy var bottomView: UIView = self.makeTwoButtonsAndDescription()
    public private(set) lazy var addBottomButton: UIButton = self.addButton()
    public private(set) lazy var quantLabel: UILabel = self.quantLabelX()
    public private(set) lazy var removeBottomButton: UIButton = self.removeButton()
    public private(set) lazy var iconProduct: UIImageView = self.iconView()
    public private(set) lazy var descProduct: UILabel = self.descView()

    // Constraints for the focus view when it gets smaller in size.
    private var regularFocusViewConstraints = [NSLayoutConstraint]()
    // Constraints for the focus view when it gets bigger in size.
    private var animatedFocusViewConstraints = [NSLayoutConstraint]()

    // MARK: - Video

    /// Video preview layer.
    private var videoPreviewLayer: AVCaptureVideoPreviewLayer?
    /// Video capture device. This may be nil when running in Simulator.
    private var captureDevice: AVCaptureDevice?
    /// Capture session.
    private lazy var captureSession: AVCaptureSession = AVCaptureSession()
    // Service used to check authorization status of the capture device
    private let permissionService = VideoPermissionService()

    /// The current torch mode on the capture device.
    private var torchMode: TorchMode = .off {
        didSet {
            guard let captureDevice = captureDevice, captureDevice.hasFlash else { return }
            guard captureDevice.isTorchModeSupported(torchMode.captureTorchMode) else { return }

            do {
                try captureDevice.lockForConfiguration()
                captureDevice.torchMode = torchMode.captureTorchMode
                captureDevice.unlockForConfiguration()
            } catch {}

            flashButton.setImage(torchMode.image, for: UIControl.State())
        }
    }

    private var frontCameraDevice: AVCaptureDevice? {
        return AVCaptureDevice.default(.builtInWideAngleCamera, for: AVMediaType.video, position: .front)
    }

    private var backCameraDevice: AVCaptureDevice? {
        return AVCaptureDevice.default(.builtInWideAngleCamera, for: AVMediaType.video, position: .back)
    }

    // MARK: - Initialization

    deinit {
        stopCapturing()
        NotificationCenter.default.removeObserver(self)
    }

    // MARK: - View lifecycle

    public override func viewDidLoad() {
        super.viewDidLoad()
        view.backgroundColor = .black
        videoPreviewLayer = AVCaptureVideoPreviewLayer(session: self.captureSession)
        videoPreviewLayer?.videoGravity = .resizeAspectFill

        guard let videoPreviewLayer = videoPreviewLayer else {
            return
        }

        view.layer.addSublayer(videoPreviewLayer)
        bottomView.addSubview(addBottomButton)
        bottomView.addSubview(quantLabel)
        bottomView.addSubview(removeBottomButton)
        bottomView.addSubview(iconProduct)
        bottomView.addSubview(descProduct)
        view.addSubviews(settingsButton, flashButton, focusView, cameraButton, bottomView)

        torchMode = .off
        focusView.isHidden = true
        setupCamera()
        setupConstraints()
        setupActions()
    }

    public override func viewDidAppear(_ animated: Bool) {
        super.viewDidAppear(animated)
        setupVideoPreviewLayerOrientation()
        animateFocusView()
    }

    public override func viewWillTransition(to size: CGSize,
                                            with coordinator: UIViewControllerTransitionCoordinator) {
        super.viewWillTransition(to: size, with: coordinator)
        coordinator.animate(
            alongsideTransition: { [weak self] _ in
                self?.setupVideoPreviewLayerOrientation()
            },
            completion: ({ [weak self] _ in
                self?.animateFocusView()
            }))
    }

    // MARK: - Video capturing

    func startCapturing() {
        guard !isSimulatorRunning else {
            return
        }

        torchMode = .off
        captureSession.startRunning()
        focusView.isHidden = false
        flashButton.isHidden = captureDevice?.position == .front
        cameraButton.isHidden = !showsCameraButton
    }

    func stopCapturing() {
        guard !isSimulatorRunning else {
            return
        }

        torchMode = .off
        captureSession.stopRunning()
        focusView.isHidden = true
        flashButton.isHidden = true
        cameraButton.isHidden = true
    }

    // MARK: - Actions

    private func setupActions() {
        flashButton.addTarget(
            self,
            action: #selector(handleFlashButtonTap),
            for: .touchUpInside
        )
        settingsButton.addTarget(
            self,
            action: #selector(handleSettingsButtonTap),
            for: .touchUpInside
        )
        cameraButton.addTarget(
            self,
            action: #selector(handleCameraButtonTap),
            for: .touchUpInside
        )

        NotificationCenter.default.addObserver(
            self,
            selector: #selector(appWillEnterForeground),
            name: UIApplication.willEnterForegroundNotification,
            object: nil
        )
    }

    /// `UIApplicationWillEnterForegroundNotification` action.
    @objc private func appWillEnterForeground() {
        torchMode = .off
        animateFocusView()
    }

    /// Opens setting to allow camera usage.
    @objc private func handleSettingsButtonTap() {
        delegate?.cameraViewControllerDidTapSettingsButton(self)
    }

    /// Swaps camera position.
    @objc private func handleCameraButtonTap() {
        swapCamera()
    }

    /// Sets the next torch mode.
    @objc private func handleFlashButtonTap() {
        torchMode = torchMode.next
    }

    // MARK: - Camera setup

    /// Sets up camera and checks for camera permissions.
    private func setupCamera() {
        permissionService.checkPersmission { [weak self] error in
            guard let strongSelf = self else {
                return
            }

            DispatchQueue.main.async { [weak self] in
                self?.settingsButton.isHidden = error == nil
            }

            if error == nil {
                strongSelf.setupSessionInput(for: .back)
                strongSelf.setupSessionOutput()
                strongSelf.delegate?.cameraViewControllerDidSetupCaptureSession(strongSelf)
            } else {
                strongSelf.delegate?.cameraViewControllerDidFailToSetupCaptureSession(strongSelf)
            }
        }
    }

    /// Sets up capture input, output and session.
    private func setupSessionInput(for position: AVCaptureDevice.Position) {
        guard !isSimulatorRunning else {
            return
        }

        guard let device = position == .front ? frontCameraDevice : backCameraDevice else {
            return
        }

        do {
            let newInput = try AVCaptureDeviceInput(device: device)
            captureDevice = device
            // Swap capture device inputs
            captureSession.beginConfiguration()
            if let currentInput = captureSession.inputs.first as? AVCaptureDeviceInput {
                captureSession.removeInput(currentInput)
            }
            captureSession.addInput(newInput)
            captureSession.commitConfiguration()
            flashButton.isHidden = position == .front
        } catch {
            delegate?.cameraViewController(self, didReceiveError: error)
            return
        }
    }

    private func setupSessionOutput() {
        guard !isSimulatorRunning else {
            return
        }

        let output = AVCaptureMetadataOutput()
        captureSession.addOutput(output)
        output.setMetadataObjectsDelegate(self, queue: DispatchQueue.main)
        output.metadataObjectTypes = metadata
        videoPreviewLayer?.session = captureSession

        view.setNeedsLayout()
    }

    /// Switch front/back camera.
    private func swapCamera() {
        guard let input = captureSession.inputs.first as? AVCaptureDeviceInput else {
            return
        }
        setupSessionInput(for: input.device.position == .back ? .front : .back)
    }

    // MARK: - Animations

    /// Performs focus view animation.
    private func animateFocusView() {
        // Restore to initial state
        focusView.layer.removeAllAnimations()
        animatedFocusViewConstraints.deactivate()
        regularFocusViewConstraints.activate()
        view.layoutIfNeeded()

        guard barCodeFocusViewType == .animated else {
            return
        }

        regularFocusViewConstraints.deactivate()
        animatedFocusViewConstraints.activate()

        UIView.animate(
            withDuration: 1.0,
            delay: 0,
            options: [.repeat, .autoreverse, .beginFromCurrentState],
            animations: ({ [weak self] in
                self?.view.layoutIfNeeded()
            }),
            completion: nil
        )
    }
}

// MARK: - Layout

private extension CameraViewController {
    func setupConstraints() {
        if #available(iOS 11.0, *) {
            NSLayoutConstraint.activate(
                flashButton.topAnchor.constraint(
                    equalTo: view.safeAreaLayoutGuide.topAnchor,
                    constant: 30
                ),
                flashButton.trailingAnchor.constraint(
                    equalTo: view.safeAreaLayoutGuide.trailingAnchor,
                    constant: -13
                ),
                cameraButton.bottomAnchor.constraint(
                    equalTo: view.safeAreaLayoutGuide.bottomAnchor,
                    constant: -30
                ),
                bottomView.bottomAnchor.constraint(
                    equalTo: view.bottomAnchor,
                    constant: 32)
            )
        } else {
            NSLayoutConstraint.activate(
                flashButton.topAnchor.constraint(equalTo: view.topAnchor, constant: 30),
                flashButton.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -13),
                cameraButton.bottomAnchor.constraint(equalTo: view.bottomAnchor, constant: -30),
                bottomView.bottomAnchor.constraint(
                    equalTo: view.bottomAnchor,
                    constant: 32)
            )
        }

        let imageButtonSize: CGFloat = 37

        NSLayoutConstraint.activate(
            flashButton.widthAnchor.constraint(equalToConstant: imageButtonSize),
            flashButton.heightAnchor.constraint(equalToConstant: imageButtonSize),

            settingsButton.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            settingsButton.centerYAnchor.constraint(equalTo: view.centerYAnchor),
            settingsButton.widthAnchor.constraint(equalToConstant: 160),
            settingsButton.heightAnchor.constraint(equalToConstant: 50),

            cameraButton.widthAnchor.constraint(equalToConstant: 48),
            cameraButton.heightAnchor.constraint(equalToConstant: 48),
            cameraButton.trailingAnchor.constraint(equalTo: flashButton.trailingAnchor),

            bottomView.widthAnchor.constraint(equalTo: view.widthAnchor, constant: 0),
            bottomView.heightAnchor.constraint(equalToConstant: 240),
            bottomView.centerXAnchor.constraint(equalTo: view.centerXAnchor),

            addBottomButton.leftAnchor.constraint(equalTo: bottomView.leftAnchor, constant: 32),
            addBottomButton.bottomAnchor.constraint(equalTo: bottomView.bottomAnchor, constant: -32),
            addBottomButton.widthAnchor.constraint(equalToConstant: 64),
            addBottomButton.heightAnchor.constraint(equalToConstant:64),

            quantLabel.centerXAnchor.constraint(equalTo: bottomView.centerXAnchor, constant: 0),
            quantLabel.bottomAnchor.constraint(equalTo: bottomView.bottomAnchor, constant: -32),
            quantLabel.widthAnchor.constraint(equalToConstant: 264),
            quantLabel.heightAnchor.constraint(equalToConstant:64),

            removeBottomButton.rightAnchor.constraint(equalTo: bottomView.rightAnchor, constant: -32),
            removeBottomButton.bottomAnchor.constraint(equalTo: bottomView.bottomAnchor, constant: -32),
            removeBottomButton.widthAnchor.constraint(equalToConstant: 64),
            removeBottomButton.heightAnchor.constraint(equalToConstant: 64),

            iconProduct.leftAnchor.constraint(equalTo: bottomView.leftAnchor, constant: 20),
            iconProduct.bottomAnchor.constraint(equalTo: addBottomButton.topAnchor, constant: -34),
            iconProduct.widthAnchor.constraint(equalToConstant: 90),
            iconProduct.heightAnchor.constraint(equalToConstant: 90),

            descProduct.leftAnchor.constraint(equalTo: iconProduct.rightAnchor, constant: 20),
            descProduct.rightAnchor.constraint(equalTo: bottomView.rightAnchor, constant: -4),
            descProduct.topAnchor.constraint(equalTo: bottomView.topAnchor),
            descProduct.bottomAnchor.constraint(equalTo: addBottomButton.topAnchor, constant: -4)
        )

        setupFocusViewConstraints()
    }

    func setupFocusViewConstraints() {
        NSLayoutConstraint.activate(
            focusView.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            focusView.centerYAnchor.constraint(equalTo: view.centerYAnchor)
        )

        let focusViewSize = barCodeFocusViewType == .oneDimension
            ? CGSize(width: 280, height: 80)
            : CGSize(width: 218, height: 150)

        regularFocusViewConstraints = [
            focusView.widthAnchor.constraint(equalToConstant: focusViewSize.width),
            focusView.heightAnchor.constraint(equalToConstant: focusViewSize.height)
        ]

        animatedFocusViewConstraints = [
            focusView.widthAnchor.constraint(equalToConstant: 280),
            focusView.heightAnchor.constraint(equalToConstant: 80)
        ]

        NSLayoutConstraint.activate(regularFocusViewConstraints)
    }

    func setupVideoPreviewLayerOrientation() {
        guard let videoPreviewLayer = videoPreviewLayer else {
            return
        }

        videoPreviewLayer.frame = view.layer.bounds

        if let connection = videoPreviewLayer.connection, connection.isVideoOrientationSupported {
            switch UIApplication.shared.statusBarOrientation {
            case .portrait:
                connection.videoOrientation = .portrait
            case .landscapeRight:
                connection.videoOrientation = .landscapeRight
            case .landscapeLeft:
                connection.videoOrientation = .landscapeLeft
            case .portraitUpsideDown:
                connection.videoOrientation = .portraitUpsideDown
            default:
                connection.videoOrientation = .portrait
            }
        }
    }
}

// MARK: - Subviews factory

private extension CameraViewController {
    func makeFocusView() -> UIView {
        let view = UIView()
        view.layer.borderColor = UIColor.white.cgColor
        view.layer.borderWidth = 2
        view.layer.cornerRadius = 5
        view.layer.shadowColor = UIColor.white.cgColor
        view.layer.shadowRadius = 10.0
        view.layer.shadowOpacity = 0.9
        view.layer.shadowOffset = CGSize.zero
        view.layer.masksToBounds = false
        return view
    }

    func makeSettingsButton() -> UIButton {
        let button = UIButton(type: .system)
        let title = NSAttributedString(
            string: localizedString("BUTTON_SETTINGS"),
            attributes: [.font: UIFont.boldSystemFont(ofSize: 17), .foregroundColor: UIColor.white]
        )
        button.setAttributedTitle(title, for: UIControl.State())
        button.sizeToFit()
        return button
    }

    func makeCameraButton() -> UIButton {
        let button = UIButton(type: .custom)
        button.setImage(imageNamed("cameraRotate"), for: UIControl.State())
        button.isHidden = !showsCameraButton
        return button
    }

    func makeTwoButtonsAndDescription() -> UIView {
        let view = UIView(frame: .zero)
        view.backgroundColor = UIColor.mainFill1
        view.addSubview(addBottomButton)
        view.addSubview(removeBottomButton)

        return view
    }

    func addButton() -> UIButton {
        let button = UIButton(type: .custom)
        button.setImage(#imageLiteral(resourceName: "addB"), for: UIControl.State())
        button.layer.cornerRadius = 32
        button.layer.masksToBounds = true
        // button.sizeToFit()
        return button
    }

    func quantLabelX() -> UILabel {
        let button = UILabel(frame: .zero)
        button.textColor = UIColor.mainText
        button.font = FontStyle.roboBold(44).new
        button.textAlignment = .center
        button.layer.masksToBounds = true
        // button.sizeToFit()
        return button
    }

    func removeButton() -> UIButton {
        let button = UIButton(type: .custom)
        button.setImage(#imageLiteral(resourceName: "remB"), for: UIControl.State())
        button.layer.cornerRadius = 32
        button.layer.masksToBounds = true
        // button.sizeToFit()
        return button
    }

    func iconView() -> UIImageView {
        let icon = UIImageView(frame: .zero)
        icon.backgroundColor = #colorLiteral(red: 0.8039215803, green: 0.8039215803, blue: 0.8039215803, alpha: 1)
        icon.layer.cornerRadius = 6
        return icon
    }

    func descView() -> UILabel {
        let label = UILabel(frame: .zero)
        label.numberOfLines = 0
        label.font = FontStyle.roboBold(18).new
        label.textColor = UIColor.mainText
        label.text = ""
        return label
    }
}

// MARK: - AVCaptureMetadataOutputObjectsDelegate

extension CameraViewController: AVCaptureMetadataOutputObjectsDelegate {
    public func metadataOutput(_ output: AVCaptureMetadataOutput,
                               didOutput metadataObjects: [AVMetadataObject],
                               from connection: AVCaptureConnection) {
        delegate?.cameraViewController(self, didOutput: metadataObjects)
    }
}
