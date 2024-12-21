import logging

class Logging:
    def __init__(self, info_output='../logs/info.log', debug_output='../logs/debug.log'):
        # ルートロガーを取得
        self.logger = logging.getLogger("commit_logger")
        self.logger.setLevel(logging.DEBUG)  # 最低レベルをDEBUGに設定

        # INFO以上のログを記録するハンドラー
        info_handler = logging.FileHandler(info_output)
        info_handler.setLevel(logging.INFO)
        info_formatter = logging.Formatter('%(asctime)s - [INFO] - %(message)s')
        info_handler.setFormatter(info_formatter)
        self.logger.addHandler(info_handler)

        # DEBUG専用のログを記録するハンドラー
        debug_handler = logging.FileHandler(debug_output)
        debug_handler.setLevel(logging.DEBUG)
        debug_formatter = logging.Formatter('%(asctime)s - [DEBUG] - %(message)s')
        debug_handler.setFormatter(debug_formatter)
        self.logger.addHandler(debug_handler)

        # コンソール出力用ハンドラー（必要に応じて追加）
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter('%(asctime)s - [CONSOLE] - %(message)s')
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
    def log_commit_time(self, commit_id, processing_time):
        """コミット処理時間をログに出力する"""
        
        # 処理時間をログに記録
        self.logger.info(f"Commit {commit_id} processed in {processing_time:.4f} seconds.")
        
    
    def log_debug_info(self, commit_id, e, error_message):
        """デバッグ情報をログに出力する"""
        self.logger.debug(f"Commit {commit_id}\n {e}\n error message :\n{error_message}")