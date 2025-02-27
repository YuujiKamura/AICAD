"""
アノテーション（注釈）モジュール

このモジュールはPDFエディターで使用されるアノテーション（注釈）関連のクラスを提供します。
注釈は線、四角形、テキストの3種類があり、それぞれPDFキャンバス上に描画されます。

主要なクラス：
- Point: 座標を表すデータクラス
- BoundingBox: 境界ボックスを表すデータクラス
- Annotation: すべての注釈の基底抽象クラス
- LineAnnotation: 線注釈クラス
- RectangleAnnotation: 四角形注釈クラス
- TextAnnotation: テキスト注釈クラス
- AnnotationManager: 注釈を管理するクラス

仕様：
1. 座標系: キャンバス座標系が使用されます（左上が原点）
2. アノテーションの選択: BoundingBoxと距離計算を使用して、クリック位置に最も近い注釈を選択
3. アノテーションの移動: 選択された注釈をdx, dyで指定された量だけ移動
4. アノテーションの描画: 各注釈クラスはdrawメソッドを持ち、キャンバスに自身を描画

注意事項：
- 注釈はPDFファイルに直接保存されず、PDFAnnotatorクラスがPDF保存時に適用
- 注釈のIDはキャンバス上の描画オブジェクトIDと連携
- 座標はすべてキャンバス座標系で管理され、PDF座標系への変換はPDF保存時に行われる
"""

import math
import logging
from typing import Tuple, Optional, List
from dataclasses import dataclass, field
from abc import ABC, abstractmethod

# ロガーの設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class Point:
    """座標を表すデータクラス"""
    x: float
    y: float

    def __add__(self, other: 'Point') -> 'Point':
        return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other: 'Point') -> 'Point':
        return Point(self.x - other.x, self.y - other.y)

    def distance_to(self, other: 'Point') -> float:
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)

@dataclass
class BoundingBox:
    """境界ボックスを表すデータクラス"""
    def __init__(self, min_point: Point, max_point: Point):
        self.min_point = min_point
        self.max_point = max_point

    def contains_point(self, point: Point, threshold: float = 5.0) -> bool:
        """点が境界ボックス内（または近く）にあるかを判定"""
        # 点が境界ボックス内にある場合
        if (self.min_point.x <= point.x <= self.max_point.x and
            self.min_point.y <= point.y <= self.max_point.y):
            return True
            
        # 点が境界ボックスの外側にある場合、最も近い境界までの距離を計算
        dx = max(self.min_point.x - point.x, 0, point.x - self.max_point.x)
        dy = max(self.min_point.y - point.y, 0, point.y - self.max_point.y)
        distance = math.sqrt(dx * dx + dy * dy)
        
        return distance <= threshold

    def move_by(self, dx: float, dy: float) -> None:
        """境界ボックスを移動"""
        self.min_point.x += dx
        self.min_point.y += dy
        self.max_point.x += dx
        self.max_point.y += dy

class Annotation(ABC):
    """注釈の基底クラス"""
    def __init__(self, color: str = "black", width: int = 1):
        self.color = color
        self.width = width
        self.id: Optional[int] = None
        self.is_selected = False
        self.highlight_id: Optional[int] = None
        self._bounding_box: Optional[BoundingBox] = None

    @property
    @abstractmethod
    def annotation_type(self) -> str:
        """注釈の種類を返す"""
        pass

    @abstractmethod
    def draw(self, canvas) -> None:
        """キャンバスに描画"""
        pass

    @abstractmethod
    def move(self, dx: float, dy: float) -> None:
        """注釈を移動"""
        pass

    @abstractmethod
    def contains_point(self, point: Point, threshold: float = 5.0) -> bool:
        """点が注釈の範囲内にあるかを判定"""
        pass

    @abstractmethod
    def get_bounding_box(self) -> BoundingBox:
        """注釈の境界ボックスを取得"""
        pass

    def show_highlight(self, canvas) -> None:
        """注釈をハイライト表示"""
        if self.highlight_id is not None:
            canvas.delete(self.highlight_id)
        bbox = self.get_bounding_box()
        self.highlight_id = canvas.create_rectangle(
            bbox.min_point.x, bbox.min_point.y,
            bbox.max_point.x, bbox.max_point.y,
            outline="blue", width=self.width + 2
        )

    def remove_highlight(self, canvas) -> None:
        """ハイライトを解除"""
        if self.highlight_id is not None:
            canvas.delete(self.highlight_id)
            self.highlight_id = None

class LineAnnotation(Annotation):
    """線注釈"""
    def __init__(self, start: Point, end: Point, color: str = "black", width: int = 1):
        super().__init__(color, width)
        self.start = start
        self.end = end
        self.is_horizontal = abs(start.y - end.y) < 2
        self.type = "line"

    @property
    def annotation_type(self) -> str:
        return "line"

    def draw(self, canvas) -> None:
        """キャンバスに線を描画"""
        if self.id is not None:
            canvas.delete(self.id)
        self.id = canvas.create_line(
            self.start.x, self.start.y,
            self.end.x, self.end.y,
            fill=self.color,
            width=self.width
        )
        logger.debug(f"線を描画: ({self.start.x}, {self.start.y}) -> ({self.end.x}, {self.end.y})")

    def move(self, dx: float, dy: float) -> None:
        """線を移動"""
        if self.is_horizontal:
            # 水平線の場合、Y座標の移動を制限
            self.start.x += dx
            self.end.x += dx
            self.start.y += dy
            self.end.y = self.start.y
        else:
            self.start.x += dx
            self.start.y += dy
            self.end.x += dx
            self.end.y += dy
        logger.debug(f"線を移動: dx={dx}, dy={dy}")

    def contains_point(self, point: Point, threshold: float = 5.0) -> bool:
        """点が線の近くにあるかを判定"""
        # 線分の長さが0の場合は点との距離を返す
        if self.start.distance_to(self.end) < 0.1:
            return self.start.distance_to(point) < threshold

        # 線分と点の距離を計算
        dx = self.end.x - self.start.x
        dy = self.end.y - self.start.y
        l2 = dx * dx + dy * dy
        
        # 点と線分の最短距離を計算
        t = max(0, min(1, ((point.x - self.start.x) * dx + 
                          (point.y - self.start.y) * dy) / l2))
        
        proj_x = self.start.x + t * dx
        proj_y = self.start.y + t * dy
        dist = math.sqrt((point.x - proj_x) ** 2 + (point.y - proj_y) ** 2)
        
        return dist < threshold

    def get_bounding_box(self) -> BoundingBox:
        """線の境界ボックスを取得"""
        return BoundingBox(
            Point(min(self.start.x, self.end.x), min(self.start.y, self.end.y)),
            Point(max(self.start.x, self.end.x), max(self.start.y, self.end.y))
        )

    def get_coords(self) -> List[float]:
        """アノテーションの座標を取得する"""
        return [self.start.x, self.start.y, self.end.x, self.end.y]

class RectangleAnnotation(Annotation):
    """四角形注釈"""
    def __init__(self, start: Point, end: Point, color: str = "black", width: int = 1):
        super().__init__(color, width)
        self.start = start
        self.end = end
        self.type = "rectangle"

    @property
    def annotation_type(self) -> str:
        return "rectangle"

    def draw(self, canvas) -> None:
        """キャンバスに四角形を描画"""
        if self.id is not None:
            canvas.delete(self.id)
        self.id = canvas.create_rectangle(
            self.start.x, self.start.y,
            self.end.x, self.end.y,
            outline=self.color,
            width=self.width
        )
        logger.debug(f"四角形を描画: ({self.start.x}, {self.start.y}) -> ({self.end.x}, {self.end.y})")

    def move(self, dx: float, dy: float) -> None:
        """四角形を移動"""
        self.start.x += dx
        self.start.y += dy
        self.end.x += dx
        self.end.y += dy
        logger.debug(f"四角形を移動: dx={dx}, dy={dy}")

    def contains_point(self, point: Point, threshold: float = 5.0) -> bool:
        """点が四角形の境界または内部にあるかを判定"""
        bbox = self.get_bounding_box()
        return bbox.contains_point(point, threshold)

    def get_bounding_box(self) -> BoundingBox:
        """四角形の境界ボックスを取得"""
        return BoundingBox(
            Point(min(self.start.x, self.end.x), min(self.start.y, self.end.y)),
            Point(max(self.start.x, self.end.x), max(self.start.y, self.end.y))
        )

    def get_coords(self) -> List[float]:
        """アノテーションの座標を取得する"""
        return [self.start.x, self.start.y, self.end.x, self.end.y]

class TextAnnotation(Annotation):
    """テキスト注釈"""
    def __init__(self, position: Point, text: str, color: str = "black", font_size: int = 12):
        super().__init__(color, 1)
        self.position = position
        self.text = text
        self.font_size = font_size
        self._text_width = 0
        self._text_height = 0
        self.type = "text"

    @property
    def annotation_type(self) -> str:
        return "text"

    def draw(self, canvas) -> None:
        """キャンバスにテキストを描画"""
        if self.id is not None:
            canvas.delete(self.id)
        self.id = canvas.create_text(
            self.position.x, self.position.y,
            text=self.text,
            fill=self.color,
            font=("Arial", self.font_size),
            anchor="nw"
        )
        # テキストの寸法を更新
        bbox = canvas.bbox(self.id)
        if bbox:
            self._text_width = bbox[2] - bbox[0]
            self._text_height = bbox[3] - bbox[1]
        logger.debug(f"テキストを描画: ({self.position.x}, {self.position.y}) text='{self.text}'")

    def move(self, dx: float, dy: float) -> None:
        """テキストを移動"""
        self.position.x += dx
        self.position.y += dy
        logger.debug(f"テキストを移動: dx={dx}, dy={dy}")

    def contains_point(self, point: Point, threshold: float = 5.0) -> bool:
        """点がテキストの範囲内にあるかを判定"""
        bbox = self.get_bounding_box()
        return bbox.contains_point(point, threshold)

    def get_bounding_box(self) -> BoundingBox:
        """テキストの境界ボックスを取得"""
        return BoundingBox(
            Point(self.position.x, self.position.y),
            Point(self.position.x + self._text_width, self.position.y + self._text_height)
        )

    def get_coords(self) -> List[float]:
        """アノテーションの座標を取得する"""
        return [self.position.x, self.position.y, 
                self.position.x + self._text_width, 
                self.position.y + self._text_height]

class AnnotationManager:
    """アノテーションの管理を行うクラス"""
    def __init__(self):
        self.annotations: List[Annotation] = []
        self.selected_annotations: List[Annotation] = []
        logger.info("AnnotationManagerを初期化しました")

    def add_annotation(self, annotation: Annotation) -> None:
        """アノテーションを追加"""
        self.annotations.append(annotation)
        logger.info(f"{annotation.__class__.__name__.lower()}を追加しました")

    def remove_annotation(self, annotation: Annotation) -> None:
        """アノテーションを削除"""
        if annotation in self.annotations:
            self.annotations.remove(annotation)
            if annotation in self.selected_annotations:
                self.selected_annotations.remove(annotation)
            logger.info(f"{annotation.__class__.__name__.lower()}を削除しました")

    def select_annotation(self, point: Point, ctrl_pressed: bool = False) -> Optional[Annotation]:
        """アノテーションを選択"""
        # 点に最も近いアノテーションを探す
        target_annotation = None
        min_distance = float('inf')
        
        for annotation in reversed(self.annotations):  # 後から追加されたものを優先
            if annotation.contains_point(point):
                # 既に選択されているアノテーションの場合、優先的に選択
                if annotation in self.selected_annotations:
                    target_annotation = annotation
                    break
                # まだ選択されていないアノテーションの場合、最も近いものを選択
                bbox = annotation.get_bounding_box()
                dist = min(
                    point.distance_to(Point(bbox.min_point.x, bbox.min_point.y)),
                    point.distance_to(Point(bbox.max_point.x, bbox.max_point.y))
                )
                if dist < min_distance:
                    min_distance = dist
                    target_annotation = annotation

        if target_annotation is None:
            if not ctrl_pressed:
                self.clear_selection()
            return None

        if ctrl_pressed:
            # Ctrl+選択: 選択状態を切り替え
            if target_annotation in self.selected_annotations:
                self.selected_annotations.remove(target_annotation)
                target_annotation.is_selected = False
                logger.info(f"{target_annotation.__class__.__name__.lower()}の選択を解除しました")
            else:
                self.selected_annotations.append(target_annotation)
                target_annotation.is_selected = True
                logger.info(f"{target_annotation.__class__.__name__.lower()}を選択しました")
        else:
            # 通常の選択: 他の選択を解除して、このアノテーションのみを選択
            self.clear_selection()
            self.selected_annotations.append(target_annotation)
            target_annotation.is_selected = True
            logger.info(f"{target_annotation.__class__.__name__.lower()}を選択しました")

        return target_annotation

    def select_multiple(self, points: List[Point], ctrl_pressed: bool = False) -> None:
        """複数のアノテーションを選択"""
        if not ctrl_pressed:
            self.clear_selection()

        for point in points:
            for annotation in reversed(self.annotations):
                if annotation.contains_point(point) and annotation not in self.selected_annotations:
                    self.selected_annotations.append(annotation)
                    annotation.is_selected = True
                    logger.info(f"{annotation.__class__.__name__.lower()}を選択しました")
                    break

    def clear_selection(self) -> None:
        """選択を解除"""
        for annotation in self.selected_annotations:
            annotation.is_selected = False
        self.selected_annotations.clear()
        logger.info("選択を解除しました")

    def move_selected(self, dx: float, dy: float) -> None:
        """選択されたアノテーションを移動"""
        for annotation in self.selected_annotations:
            annotation.move(dx, dy)
        logger.info("選択されたアノテーションを移動しました")

    def draw_all(self, canvas) -> None:
        """全ての注釈を描画"""
        for annotation in self.annotations:
            annotation.draw(canvas)
            if annotation.is_selected:
                annotation.show_highlight(canvas) 