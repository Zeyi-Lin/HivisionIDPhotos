import gradio as gr
import os
import pathlib


def load_description(fp):
    with open(fp, "r", encoding="utf-8") as f:
        content = f.read()
    return content


def create_ui(processor, root_dir):
    size_list_dict_CN, size_list_dict_EN, color_list_dict_CN, color_list_dict_EN = (
        processor.size_list_dict_CN,
        processor.size_list_dict_EN,
        processor.color_list_dict_CN,
        processor.color_list_dict_EN,
    )

    size_mode_CN = ["尺寸列表", "只换底", "自定义尺寸"]
    size_mode_EN = ["Size List", "Only Change Background", "Custom Size"]

    size_list_CN = list(size_list_dict_CN.keys())
    size_list_EN = list(size_list_dict_EN.keys())

    colors_CN = ["蓝色", "白色", "红色", "黑色", "深蓝色", "自定义底色"]
    colors_EN = ["Blue", "White", "Red", "Black", "Dark blue", "Custom Color"]

    watermark_CN = ["不添加", "添加"]
    watermark_EN = ["Not Add", "Add"]

    render_CN = ["纯色", "上下渐变 (白)", "中心渐变 (白)"]
    render_EN = ["Solid Color", "Up-Down Gradient (White)", "Center Gradient (White)"]

    image_kb_CN = ["不设置", "自定义"]
    image_kb_EN = ["Not Set", "Custom"]

    css = """
        #col-left {
            margin: 0 auto;
            max-width: 430px;
        }
        #col-mid {
            margin: 0 auto;
            max-width: 430px;
        }
        #col-right {
            margin: 0 auto;
            max-width: 430px;
        }
        #col-showcase {
            margin: 0 auto;
            max-width: 1100px;
        }
        #button {
            color: blue;
        }
        """

    demo = gr.Blocks(title="HivisionIDPhotos", css=css)

    with demo:
        gr.HTML(load_description(os.path.join(root_dir, "assets/title.md")))
        with gr.Row():
            # ------------ 左半边 UI ----------------
            with gr.Column():
                img_input = gr.Image(height=400)

                with gr.Row():
                    # 语言选择器
                    language = ["中文", "English"]
                    language_options = gr.Dropdown(
                        choices=language,
                        label="Language",
                        value="中文",
                        elem_id="language",
                    )

                    face_detect_model_options = gr.Dropdown(
                        choices=["mtcnn", "face++ (联网API)"],
                        label="人脸检测模型",
                        value="mtcnn",
                        elem_id="matting_model",
                    )
                    matting_model_options = gr.Dropdown(
                        choices=["modnet_photographic_portrait_matting"],
                        label="抠图模型",
                        value="modnet_photographic_portrait_matting",
                        elem_id="matting_model",
                    )

                with gr.Tab("核心参数") as key_parameter_tab:
                    mode_options = gr.Radio(
                        choices=size_mode_CN,
                        label="证件照尺寸选项",
                        value="尺寸列表",
                        elem_id="size",
                    )

                    with gr.Row(visible=True) as size_list_row:
                        size_list_options = gr.Dropdown(
                            choices=size_list_CN,
                            label="预设尺寸",
                            value=size_list_CN[0],
                            elem_id="size_list",
                        )

                    with gr.Row(visible=False) as custom_size:
                        custom_size_height = gr.Number(
                            value=413, label="height", interactive=True
                        )
                        custom_size_width = gr.Number(
                            value=295, label="width", interactive=True
                        )

                    color_options = gr.Radio(
                        choices=colors_CN, label="背景色", value="蓝色", elem_id="color"
                    )

                    with gr.Row(visible=False) as custom_color:
                        custom_color_R = gr.Number(value=0, label="R", interactive=True)
                        custom_color_G = gr.Number(value=0, label="G", interactive=True)
                        custom_color_B = gr.Number(value=0, label="B", interactive=True)

                    render_options = gr.Radio(
                        choices=render_CN,
                        label="渲染方式",
                        value="纯色",
                        elem_id="render",
                    )

                with gr.Tab("高级参数") as advance_parameter_tab:
                    head_measure_ratio_option = gr.Slider(
                        minimum=0.1,
                        maximum=0.5,
                        value=0.2,
                        step=0.01,
                        label="面部比例",
                        interactive=True,
                    )
                    top_distance_option = gr.Slider(
                        minimum=0.02,
                        maximum=0.5,
                        value=0.12,
                        step=0.01,
                        label="头距顶距离",
                        interactive=True,
                    )

                    image_kb_options = gr.Radio(
                        choices=image_kb_CN,
                        label="设置 KB 大小（结果在右边最底的组件下载）",
                        value="不设置",
                        elem_id="image_kb",
                    )

                    with gr.Row(visible=False) as custom_image_kb:
                        custom_image_kb_size = gr.Slider(
                            minimum=10,
                            maximum=1000,
                            value=50,
                            label="KB 大小",
                            interactive=True,
                        )

                with gr.Tab("水印") as watermark_parameter_tab:
                    watermark_options = gr.Radio(
                        choices=watermark_CN,
                        label="水印",
                        value="不添加",
                        elem_id="watermark",
                    )

                    with gr.Row():
                        watermark_text_options = gr.Text(
                            max_length=10,
                            label="水印文字",
                            value="Hello",
                            placeholder="请输入水印文字（最多10个字符）",
                            elem_id="watermark_text",
                            interactive=False,
                        )
                        watermark_text_color = gr.ColorPicker(
                            label="水印颜色",
                            interactive=False,
                            value="#FFFFFF",
                        )

                    watermark_text_size = gr.Slider(
                        minimum=10,
                        maximum=100,
                        value=20,
                        label="文字大小",
                        interactive=False,
                        step=1,
                    )

                    watermark_text_opacity = gr.Slider(
                        minimum=0,
                        maximum=1,
                        value=0.15,
                        label="水印透明度",
                        interactive=False,
                        step=0.01,
                    )

                    watermark_text_angle = gr.Slider(
                        minimum=0,
                        maximum=360,
                        value=30,
                        label="水印角度",
                        interactive=False,
                        step=1,
                    )

                    watermark_text_space = gr.Slider(
                        minimum=10,
                        maximum=200,
                        value=25,
                        label="水印间距",
                        interactive=False,
                        step=1,
                    )

                    def update_watermark_text_visibility(choice):
                        return [
                            gr.update(interactive=(choice == "添加" or choice == "Add"))
                        ] * 6

                    watermark_options.change(
                        fn=update_watermark_text_visibility,
                        inputs=[watermark_options],
                        outputs=[
                            watermark_text_options,
                            watermark_text_color,
                            watermark_text_size,
                            watermark_text_opacity,
                            watermark_text_angle,
                            watermark_text_space,
                        ],
                    )

                img_but = gr.Button("开始制作")

                example_images = gr.Examples(
                    inputs=[img_input],
                    examples=[
                        [path.as_posix()]
                        for path in sorted(
                            pathlib.Path(os.path.join(root_dir, "demo/images")).rglob(
                                "*.jpg"
                            )
                        )
                    ],
                )

            # ---------------- 右半边 UI ----------------
            with gr.Column():
                notification = gr.Text(label="状态", visible=False)
                with gr.Row():
                    img_output_standard = gr.Image(
                        label="标准照", height=350, format="jpeg"
                    )
                    img_output_standard_hd = gr.Image(
                        label="高清照", height=350, format="jpeg"
                    )
                img_output_layout = gr.Image(
                    label="六寸排版照", height=350, format="jpeg"
                )
                file_download = gr.File(label="下载调整 KB 大小后的照片", visible=False)

            # ---------------- 设置隐藏/显示组件 ----------------
            def change_language(language):
                if language == "中文":
                    return {
                        size_list_options: gr.update(
                            label="预设尺寸",
                            choices=size_list_CN,
                            value=size_list_CN[0],
                        ),
                        mode_options: gr.update(
                            label="证件照尺寸选项",
                            choices=size_mode_CN,
                            value="尺寸列表",
                        ),
                        color_options: gr.update(
                            label="背景色",
                            choices=colors_CN,
                            value="蓝色",
                        ),
                        img_but: gr.update(value="开始制作"),
                        render_options: gr.update(
                            label="渲染方式",
                            choices=render_CN,
                            value="纯色",
                        ),
                        image_kb_options: gr.update(
                            label="设置 KB 大小（结果在右边最底的组件下载）",
                            choices=image_kb_CN,
                            value="不设置",
                        ),
                        matting_model_options: gr.update(label="抠图模型"),
                        face_detect_model_options: gr.update(label="人脸检测模型"),
                        custom_image_kb_size: gr.update(label="KB 大小"),
                        notification: gr.update(label="状态"),
                        img_output_standard: gr.update(label="标准照"),
                        img_output_standard_hd: gr.update(label="高清照"),
                        img_output_layout: gr.update(label="六寸排版照"),
                        file_download: gr.update(label="下载调整 KB 大小后的照片"),
                        head_measure_ratio_option: gr.update(label="面部比例"),
                        top_distance_option: gr.update(label="头距顶距离"),
                        key_parameter_tab: gr.update(label="核心参数"),
                        advance_parameter_tab: gr.update(label="高级参数"),
                        watermark_parameter_tab: gr.update(label="水印"),
                        watermark_text_options: gr.update(label="水印文字"),
                        watermark_text_color: gr.update(label="水印颜色"),
                        watermark_text_size: gr.update(label="文字大小"),
                        watermark_text_opacity: gr.update(label="水印透明度"),
                        watermark_text_angle: gr.update(label="水印角度"),
                        watermark_text_space: gr.update(label="水印间距"),
                        watermark_options: gr.update(
                            label="水印", value="不添加", choices=watermark_CN
                        ),
                    }

                elif language == "English":
                    return {
                        size_list_options: gr.update(
                            label="Default size",
                            choices=size_list_EN,
                            value=size_list_EN[0],
                        ),
                        mode_options: gr.update(
                            label="ID photo size options",
                            choices=size_mode_EN,
                            value="Size List",
                        ),
                        color_options: gr.update(
                            label="Background color",
                            choices=colors_EN,
                            value="Blue",
                        ),
                        img_but: gr.update(value="Start"),
                        render_options: gr.update(
                            label="Rendering mode",
                            choices=render_EN,
                            value="Solid Color",
                        ),
                        image_kb_options: gr.update(
                            label="Set KB size (Download in the bottom right)",
                            choices=image_kb_EN,
                            value="Not Set",
                        ),
                        matting_model_options: gr.update(label="Matting model"),
                        face_detect_model_options: gr.update(label="Face detect model"),
                        custom_image_kb_size: gr.update(label="KB size"),
                        notification: gr.update(label="Status"),
                        img_output_standard: gr.update(label="Standard photo"),
                        img_output_standard_hd: gr.update(label="HD photo"),
                        img_output_layout: gr.update(label="Layout photo"),
                        file_download: gr.update(
                            label="Download the photo after adjusting the KB size"
                        ),
                        head_measure_ratio_option: gr.update(label="Head ratio"),
                        top_distance_option: gr.update(label="Top distance"),
                        key_parameter_tab: gr.update(label="Key Parameters"),
                        advance_parameter_tab: gr.update(label="Advance Parameters"),
                        watermark_parameter_tab: gr.update(label="Watermark"),
                        watermark_text_options: gr.update(label="Text"),
                        watermark_text_color: gr.update(label="Color"),
                        watermark_text_size: gr.update(label="Size"),
                        watermark_text_opacity: gr.update(label="Opacity"),
                        watermark_text_angle: gr.update(label="Angle"),
                        watermark_text_space: gr.update(label="Space"),
                        watermark_options: gr.update(
                            label="Watermark", value="Not Add", choices=watermark_EN
                        ),
                    }

            def change_color(colors):
                if colors == "自定义底色" or colors == "Custom Color":
                    return {custom_color: gr.update(visible=True)}
                else:
                    return {custom_color: gr.update(visible=False)}

            def change_size_mode(size_option_item):
                if (
                    size_option_item == "自定义尺寸"
                    or size_option_item == "Custom Size"
                ):
                    return {
                        custom_size: gr.update(visible=True),
                        size_list_row: gr.update(visible=False),
                    }
                elif (
                    size_option_item == "只换底"
                    or size_option_item == "Only Change Background"
                ):
                    return {
                        custom_size: gr.update(visible=False),
                        size_list_row: gr.update(visible=False),
                    }
                else:
                    return {
                        custom_size: gr.update(visible=False),
                        size_list_row: gr.update(visible=True),
                    }

            def change_image_kb(image_kb_option):
                if image_kb_option == "自定义" or image_kb_option == "Custom":
                    return {custom_image_kb: gr.update(visible=True)}
                else:
                    return {custom_image_kb: gr.update(visible=False)}

            # ---------------- 绑定事件 ----------------
            language_options.input(
                change_language,
                inputs=[language_options],
                outputs=[
                    size_list_options,
                    mode_options,
                    color_options,
                    img_but,
                    render_options,
                    image_kb_options,
                    matting_model_options,
                    face_detect_model_options,
                    custom_image_kb_size,
                    notification,
                    img_output_standard,
                    img_output_standard_hd,
                    img_output_layout,
                    file_download,
                    head_measure_ratio_option,
                    top_distance_option,
                    key_parameter_tab,
                    advance_parameter_tab,
                    watermark_parameter_tab,
                    watermark_text_options,
                    watermark_text_color,
                    watermark_text_size,
                    watermark_text_opacity,
                    watermark_text_angle,
                    watermark_text_space,
                    watermark_options,
                ],
            )

            color_options.input(
                change_color, inputs=[color_options], outputs=[custom_color]
            )

            mode_options.input(
                change_size_mode,
                inputs=[mode_options],
                outputs=[custom_size, size_list_row],
            )

            image_kb_options.input(
                change_image_kb, inputs=[image_kb_options], outputs=[custom_image_kb]
            )

            img_but.click(
                processor.process,
                inputs=[
                    img_input,
                    mode_options,
                    size_list_options,
                    color_options,
                    render_options,
                    image_kb_options,
                    custom_color_R,
                    custom_color_G,
                    custom_color_B,
                    custom_size_height,
                    custom_size_width,
                    custom_image_kb_size,
                    language_options,
                    matting_model_options,
                    watermark_options,
                    watermark_text_options,
                    watermark_text_color,
                    watermark_text_size,
                    watermark_text_opacity,
                    watermark_text_angle,
                    watermark_text_space,
                    face_detect_model_options,
                    head_measure_ratio_option,
                    top_distance_option,
                ],
                outputs=[
                    img_output_standard,
                    img_output_standard_hd,
                    img_output_layout,
                    notification,
                    file_download,
                ],
            )

    return demo
