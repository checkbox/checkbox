#include <QHBoxLayout>
#include <QGraphicsScene>
#include <QGraphicsEllipseItem>
#include <QGraphicsView>
#include <QGraphicsTextItem>
#include <QLabel>

#include "step.h"

#define STEP_COLOR "#DD4814"
#define BORDER_COLOR "#000000"
#define TEXT_COLOR "#FFFFFF"

Step::Step(QWidget *parent, QString text, QString index)
{
    setParent(parent);
    setFixedWidth(470);
    QHBoxLayout *layout = new QHBoxLayout(this);

    if (index != "") {
        QGraphicsScene *scene = new QGraphicsScene(0, 0, 25, 25);
        QGraphicsEllipseItem *item = new QGraphicsEllipseItem(0, 0, 20, 20);
        item->setBrush(QBrush(STEP_COLOR));
        QPen pen;
        pen.setColor(BORDER_COLOR);
        pen.setWidthF(1.5);
        item->setPen(pen);
        item->setPos(1,1);
        scene->addItem(item);
        item->setPos(1,1);
        QGraphicsView *view = new QGraphicsView(scene);
        view->setRenderHint(QPainter::Antialiasing, true);
        view->setRenderHint(QPainter::TextAntialiasing, true);
        view->setFrameShape(QFrame::NoFrame);
        view->setBackgroundRole(QPalette::NoRole);
        view->setFixedSize(25, 25);
        QGraphicsTextItem *text = new QGraphicsTextItem(item, scene);
        text->setHtml("<center>"+index+"</center>");
        text->setPos(1,-3);
        text->setTextWidth(18);
        text->setDefaultTextColor(TEXT_COLOR);
        QFont boldFont;
        boldFont.setWeight(QFont::Bold);
        text->setFont(boldFont);
        layout->addWidget(view);
    } else {
        QWidget *widget = new QWidget(this);
        widget->setFixedWidth(50);
        layout->addWidget(widget);
    }

    QLabel *label = new QLabel(text);
    label->setWordWrap(true);
    label->setSizePolicy(QSizePolicy::Expanding, QSizePolicy::Maximum);
    layout->addWidget(label);
    show();

}

Step::~Step() {
    hide();
}
