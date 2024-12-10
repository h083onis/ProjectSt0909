import networkx as nx


class GraphSearch():
    def __init__(self):
        self.graph = nx.DiGraph()  # 初期化時に空のグラフを作成
    
    def read_dot(self, dot_path):
        """DOTファイルを読み込み、DiGraphを作成"""
        self.graph = nx.DiGraph(nx.drawing.nx_pydot.read_dot(dot_path))
    
    def read_set(self, relation_set):
        self.graph.add_edges_from(relation_set)
    
    def find_files_with_keyword(self, target_node, keyword="Test"):
        """
        特定のノードから指定キーワードを含むファイルを探索
        Args:
            target_node (str): 探索開始ノード
            keyword (str): 探索対象のキーワード (デフォルトは "Test")
        Returns:
            list[tuple]: キーワードを含むファイル名とその深さ ([(file_name, depth), ...])
        """
        results = []
        stack = [(target_node, 0)]  # スタックにノードと深さを保持
        visited = set()  # 訪問済みノードを記録

        while stack:
            current_node, depth = stack.pop()
            if current_node in visited:
                continue
            visited.add(current_node)

            # キーワードを含むノードを検出
            if keyword in current_node and depth != 0:
                results.append({"fqcn_name":current_node, "depth":depth})
            
            # 親ノードをスタックに追加
            stack.extend((predecessor, depth + 1) for predecessor in self.graph.predecessors(current_node))
        
        return results
